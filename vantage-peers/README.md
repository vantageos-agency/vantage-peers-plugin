# vantage-peers plugin

Plug-and-play kit for [VantagePeers](https://vantagepeers.com) MCP. Install this plugin after deploying your VantagePeers MCP server to make any Claude Code workspace VP-fluent immediately: expert agent, 5 autonomous skills, CLAUDE.md protocol template, and .mcp.json config template — all bundled and ready.

---

## What this plugin does

The `vantage-peers` plugin wires Claude Code to a VantagePeers MCP backend. It provides an expert agent that knows all ~82 VP tools and their correct usage, five skills covering the full orchestrator lifecycle (morning planning, messaging, session snapshots, day close, and setup verification), and two templates that make new workspace onboarding a 4-step process instead of a half-day configuration exercise. Designed for the VantageOS agent swarm workflow where multiple orchestrators (Pi, Sigma, Tau, etc.) coordinate via shared memory, tasks, missions, and real-time messaging.

---

## Prerequisites

- A deployed VantagePeers MCP server. Two options:
  - **Railway one-click** — deploy template at [vantagepeers.com/deploy](https://vantagepeers.com/docs/deploy) (recommended, ~3 minutes)
  - **Convex self-host** — follow [vantagepeers.com/docs/self-host](https://vantagepeers.com/docs/self-host)
- Claude Code with plugins support
- Your Railway deployment URL and bearer secret (set as `BEARER_SECRET` env var in Railway)

---

## Install

### Option A — Marketplace install (recommended)

```
/plugin marketplace add vantageos-agency/plugins
/plugin install vantage-peers@vantageos-plugins
```

### Option B — Manual clone

For air-gapped or offline setups, or when plugin install is unavailable:

```bash
git clone https://github.com/vantageos-agency/plugins.git
cp -r plugins/vantage-peers ~/.claude/plugins/
```

The `vantage-peers/` folder is fully self-contained — no symlinks, no cross-folder file references. Verified: `find vantage-peers/ -type l` returns 0 results.

---

## Quick start

**Step 1 — Deploy MCP server**

Deploy to Railway using the one-click template. Note your deployment URL (e.g. `https://vantage-peers-abc123.railway.app`) and the `BEARER_SECRET` you configured.

**Step 2 — Configure .mcp.json**

Copy `templates/.mcp.json.template` to `.mcp.json` in your workspace (or to `~/.claude.json` for global access):

```json
{
  "mcpServers": {
    "vantage-peers": {
      "type": "http",
      "url": "https://your-deployment.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer your-bearer-secret"
      }
    }
  }
}
```

Restart Claude Code after saving.

**Step 3 — Append CLAUDE.md template**

Append the contents of `templates/CLAUDE.md.append` to the bottom of your workspace `CLAUDE.md`. This installs the VantagePeers workflow protocols (recall-before-assumptions, task protocol, namespace conventions) into your orchestrator's operating instructions.

**Step 4 — Run init skill**

```
/vantage-peers-init
```

All 3 checks (registration, connectivity, auth) must show PASS. The skill outputs a report with specific fixes for any failure.

---

## Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| `/vantage-peers-init` | "verify VP setup", "VP smoke test", "init vantage-peers", "test VP connection" | Verifies MCP registration, tests `/health` endpoint, smoke-tests auth via `recall`. Outputs PASS/FAIL report with fixes. |
| `/check-messages` | "check messages", "any messages", "inbox", "peers" | Polls unread messages, marks read, auto-picks next task (autonomous mode) or displays for human. |
| `/daily-start` | "start the day", "morning plan", "daily planning", "what's on my plate" | Session-start routine: loads context from VP, presents routines (human) or auto-picks highest-priority task (autonomous). |
| `/close-day` | "close day", "end of day", "wrap up", "close session" | Updates task statuses, writes diary entry, stores session summary, calls `set_summary` to closed. |
| `/pre-compact` | "save context", "before compaction", "snapshot session", "/pre-compact" | Saves full session state (missions + tasks + blockers + 3-line summary) as memory + briefing note before Claude Code compaction. |

---

## Agent

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `vantage-peers-expert` | "store this", "recall X", "create task", "set up VP", "what's in memory", "send message to pi", "VP namespace", "fix pattern" | Full VP MCP specialist. Knows all tools, namespaces, memory types, task protocol, T-VERIFY doctrine. Routes to skills for lifecycle operations. |

---

## Templates

| Template | Location | Use |
|----------|----------|-----|
| `CLAUDE.md.append` | `templates/CLAUDE.md.append` | Append to workspace CLAUDE.md to install VP workflow protocols |
| `.mcp.json.template` | `templates/.mcp.json.template` | Copy and fill in URL + bearer secret for MCP registration |

---

## Hooks

Hooks folder is intentionally empty in v1.0.0. v1.1 will add:
- `enforce-mcp-first.py` — blocks VP tool calls without a registered MCP server

---

## Sellable as

Any agency or developer running a Claude Code agent swarm who needs persistent shared memory, multi-orchestrator messaging, and task coordination out of the box. Install once, connect to a Railway-hosted MCP server, and every orchestrator in the swarm (Pi, Sigma, Tau, etc.) gains full VP fluency without manual configuration. Target buyers: VantageOS resellers, technical founders managing autonomous agent pipelines, and agencies delivering Claude Code-based automation to clients.

Part of the VantagePeers ecosystem — published by VantageOS at vantagepeers.com.

---

## Links

- VantagePeers docs: [vantagepeers.com/docs](https://vantagepeers.com/docs)
- Railway deploy template: [vantagepeers.com/deploy](https://vantagepeers.com/docs/deploy)
- Plugin source: [github.com/vantageos-agency/plugins](https://github.com/vantageos-agency/plugins)
- VantageOS agency: [vantageos.agency](https://vantageos.agency)

---

Built by [vantageos-agency](https://vantageos.agency).
