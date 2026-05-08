---
name: vantage-peers-init
description: >
  Verify and smoke-test the VantagePeers MCP setup in the current workspace.
  Use this skill whenever the user says "verify VP setup", "test vantage-peers",
  "VP smoke test", "init vantage-peers", "/vantage-peers-init", "check VP connection",
  "is VP configured", "test my VP install", "vantage-peers health check" --
  even if they don't say "vantage-peers-init" explicitly.
allowed-tools: mcp__vantage-peers__* Bash Read
metadata:
  version: "1.0.0"
  user-invocable: true
license: Proprietary
---

Verify that VantagePeers MCP is correctly registered, reachable, and authenticated in the current workspace. Outputs a PASS/FAIL report with suggested fixes.

## TL;DR

Runs three sequential checks (MCP registration, HTTP connectivity, auth smoke test) and prints a PASS/FAIL report with prescriptive fixes for any failure. Safe to run at any time — read-only diagnostic, creates no data.

## Decision Tree

```
Is vantage-peers in .mcp.json or ~/.claude.json?
├── FOUND → CHECK 1 PASS. Extract URL. Proceed to CHECK 2.
└── NOT FOUND → CHECK 1 FAIL → Fix A (add to .mcp.json). Still run CHECK 2 + CHECK 3 for completeness.

Does the health endpoint respond HTTP 200?
├── 200 + version field present → CHECK 2 PASS
├── 200 + version present but unexpected value → CHECK 2 WARN (log and continue — may still work)
└── Non-200 or no response → CHECK 2 FAIL → Fix B (verify Railway deployment + URL format)

Does mcp__vantage-peers__recall return a valid array?
├── Array returned (even empty []) → CHECK 3 PASS
└── Error or timeout → CHECK 3 FAIL → Fix C (verify bearer token matches Railway env var)
```

## WORKFLOW

**Step 1 — Detect orchestrator identity**

Read the first 30 lines of `CLAUDE.md` in the current workspace:
```bash
head -30 CLAUDE.md 2>/dev/null || head -30 ~/CLAUDE.md 2>/dev/null || echo "NO_CLAUDE_MD"
```

Extract:
- `ORCHESTRATOR_NAME` — e.g. "sigma", "pi", "tau"
- `INSTANCE_ID` — e.g. "sigma-vps-1"
- `WORKSPACE` — the current working directory

If CLAUDE.md is not found: note it as a warning (not a blocker for MCP tests).

**Step 2 — Check MCP registration**

Look for vantage-peers in MCP config. Check both locations:

```bash
# Check project-level .mcp.json (try jq first, fall back to python3)
if command -v jq &>/dev/null; then
  cat .mcp.json 2>/dev/null | jq -r 'if .mcpServers["vantage-peers"] then "FOUND" else "MISSING" end' 2>/dev/null || echo "NO_MCP_JSON"
else
  cat .mcp.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('FOUND' if 'vantage-peers' in d.get('mcpServers',{}) else 'MISSING')" 2>/dev/null || echo "NO_MCP_JSON"
fi

# Check global claude config
if command -v jq &>/dev/null; then
  cat ~/.claude.json 2>/dev/null | jq -r 'if .mcpServers["vantage-peers"] then "FOUND" else "MISSING" end' 2>/dev/null || echo "NO_CLAUDE_JSON"
else
  cat ~/.claude.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); servers=d.get('mcpServers',{}); print('FOUND' if 'vantage-peers' in servers else 'MISSING')" 2>/dev/null || echo "NO_CLAUDE_JSON"
fi
```

Rules:
- `FOUND` in either location = CHECK 1 PASS
- `MISSING` in both = CHECK 1 FAIL → fix: run Step 5 fix A

If FOUND, extract the URL:
```bash
if command -v jq &>/dev/null; then
  cat .mcp.json 2>/dev/null | jq -r '.mcpServers["vantage-peers"].url // "NO_URL"'
else
  cat .mcp.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); s=d.get('mcpServers',{}).get('vantage-peers',{}); print(s.get('url','NO_URL'))"
fi
```

**Step 3 — Test HTTP connectivity**

Using the URL from Step 2 (strip `/mcp` suffix to get base URL):

```bash
BASE_URL=$(echo "$VP_URL" | sed 's|/mcp$||')
curl -s -o /tmp/vp_health.json -w "%{http_code}" "${BASE_URL}/health" 2>/dev/null
```

Check response:
- HTTP 200 = connectivity OK
- Parse JSON: check for any `version` field present
- If `version` field present → CHECK 2 PASS (version confirmed — exact value is not enforced)
- If `version` field absent from otherwise valid response → CHECK 2 WARN (unexpected response shape)
- HTTP non-200 or no response → CHECK 2 FAIL → fix: run Step 5 fix B

**Step 4 — MCP auth smoke test**

Invoke the `recall` tool directly through the MCP layer:

```
mcp__vantage-peers__recall query="test" limit=1
```

Expected: an array response (empty `[]` is acceptable — it means auth works but no matching memories exist).
Failure: any error, timeout, or non-array response → CHECK 3 FAIL → fix: run Step 5 fix C

**Step 5 — Output verification report**

Print the full report:

```
VANTAGE-PEERS INIT REPORT
=========================
Date      : <ISO datetime>
Workspace : <WORKSPACE>
Orchestrator : <ORCHESTRATOR_NAME> / <INSTANCE_ID>

CHECK 1 — MCP Registration
  Source   : <.mcp.json | ~/.claude.json | NOT FOUND>
  URL      : <url or N/A>
  Status   : <PASS | FAIL>

CHECK 2 — HTTP Connectivity
  Endpoint : <BASE_URL>/health
  HTTP     : <status code>
  Version  : <version string or N/A>
  Status   : <PASS | WARN | FAIL>

CHECK 3 — Auth Smoke Test
  Tool     : mcp__vantage-peers__recall query="test"
  Response : <array (N results) | ERROR: <message>>
  Status   : <PASS | FAIL>

OVERALL  : <ALL PASS | X CHECK(S) FAILED>
```

Then print suggested fixes for any FAIL:

**Fix A — MCP not registered**
Add to `.mcp.json` in current workspace (or `~/.claude.json` for global):
```json
{
  "mcpServers": {
    "vantage-peers": {
      "type": "http",
      "url": "<YOUR_RAILWAY_URL>/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_BEARER_SECRET>"
      }
    }
  }
}
```
Then restart Claude Code.

**Fix B — Connectivity failure**
- Confirm Railway deployment is running: visit `<BASE_URL>/health` in a browser.
- If Railway is sleeping (free tier), trigger a wake: `curl <BASE_URL>/health`.
- Verify the URL in .mcp.json ends with `/mcp` (not the base URL).
- Check `BEARER_SECRET` env var is set in Railway dashboard.

**Fix C — Auth failure**
- Verify the `Authorization: Bearer <token>` header value matches `BEARER_SECRET` in your Railway environment variables.
- Rotate the secret if compromised: update Railway env var + update `.mcp.json` header + restart Claude Code.

## RULES

- This skill is read-only diagnostic — it never modifies config files.
- Always run all three checks even if CHECK 1 fails (connectivity and auth may still reveal useful info).
- WARN status on CHECK 2 (unexpected version or response shape) is not a blocker — log it and continue.
- If CLAUDE.md is missing, note it in the report but do not fail the VP checks on that basis alone.
- The smoke test in CHECK 3 uses `recall query="test"` because it is the lowest-cost read operation and does not create any data.

## When Things Go Wrong

| Error scenario | Likely cause | Fix |
|----------------|--------------|-----|
| CHECK 1 FAIL but .mcp.json exists | Key is named differently (e.g. `"vantage-memory"` instead of `"vantage-peers"`) | Check the exact key name: `cat .mcp.json | jq '.mcpServers | keys'`; rename to `vantage-peers` + restart Claude Code |
| CHECK 2 FAIL with HTTP 401 | Bearer token in .mcp.json doesn't match `BEARER_SECRET` in Railway | Update the `Authorization` header in `.mcp.json` to match the Railway env var value |
| CHECK 3 returns tool-not-found error | Claude Code session hasn't reloaded the MCP config after editing .mcp.json | Restart Claude Code (Cmd+Shift+P → "Restart Claude") to pick up updated MCP registrations |

## Sellable As

Part of `vantage-peers` plugin v1.0.0. Available via `/plugin install vantage-peers` after deploying VantagePeers MCP server (Railway template or Convex self-host).
