---
name: pre-compact
description: >
  Save the current session state to VantagePeers (memory + briefing note)
  before Claude Code compaction. Use this skill whenever the user says
  "save context", "save session", "before compaction", "I will compact",
  "snapshot session", "context save", "freeze state", "/pre-compact" --
  even if they do not say "pre-compact" explicitly.
  Sauvegarde l'etat de session dans VantagePeers avant compaction Claude Code.
  Utilise ce skill quand l'utilisateur dit "sauvegarde le contexte",
  "avant compaction", "je vais compacter", "snapshot session", "fige l'etat".
allowed-tools: mcp__vantage-peers__* Bash Read
metadata:
  version: "1.0.0"
  user-invocable: true
license: Proprietary
---

Persist a standardized session snapshot (memory + briefing note) to VantagePeers so any orchestrator can resume exactly where it left off after compaction.

## TL;DR

Captures the full session state (active missions, in-progress tasks, blockers, recent commits, 3-line summary) into a VantagePeers memory + briefing note so any orchestrator can resume exactly where it left off after compaction.

## Decision Tree

```
Is this a human or autonomous session?
├── Human mode (operator triggered "save context" / "je vais compacter")
│   └── Run Steps 1-6. Output minimal 5-line summary. Wait for operator to proceed.
└── Autonomous mode (orchestrator triggered pre-compact before self-compacting)
    └── Run Steps 1-6. Output verbose summary with 3-line resume. Exit to standby.

Are optional data sources available?
├── git log accessible → include recentCommits in payload
└── git log fails → set recentCommits=[] (empty is valid, not a blocker)

Is the briefing note schema valid?
├── memId returned from store_memory → insert into briefing note content before calling create_briefing_note
└── store_memory fails → abort and report error (do not create a briefing note with a missing memory link)
```

## WORKFLOW

**Step 1 — Detect mode (human vs autonomous)**

- Read the first 20 lines of `CLAUDE.md` in the current workspace.
- If CLAUDE.md header says "You are Pi" AND the workspace is clearly an interactive human operator session → **HUMAN MODE**.
- Else (sigma, alpha, lambda, victor, tau, phi, omega, eta, zeta, or any client orchestrator on any VPS) → **AUTONOMOUS MODE**.
- Default = autonomous mode.

**Step 2 — Fetch session state (run in parallel)**

```bash
# Detect <orchestrator>, <instanceId>, <bu> from CLAUDE.md + hostname
# Then run all four queries simultaneously:
mcp__vantage-peers__list_missions   pilot=<orchestrator>  status=execute,plan
mcp__vantage-peers__list_tasks      assignedTo=<orchestrator>  status=in_progress
mcp__vantage-peers__list_tasks      assignedTo=<orchestrator>  status=todo  # filter urgent+high, limit 10
mcp__vantage-peers__recall          query="active blockers pending decisions"  namespace=project/<bu>  limit=5
git log --oneline -10               # best-effort — empty is acceptable
```

**Step 3 — Build memory payload (state-of-the-session)**

Construct the JSON payload from the data collected in Step 2.

Required keys: `schemaVersion`, `snapshotType`, `createdAt`, `orchestrator`, `instanceId`, `bu`, `summary3Lines`.
Optional keys: `activeMissions`, `inProgressTasks`, `urgentTodoTasks`, `blockers`, `pendingDecisions`, `recentCommits`.

```json
{
  "schemaVersion": "1.0.0",
  "snapshotType": "state-of-the-session",
  "createdAt": "<ISO-8601 datetime with TZ>",
  "orchestrator": "<orchestrator>",
  "instanceId": "<instanceId>",
  "bu": "<bu>",
  "activeMissions": [
    { "id": "<mission-id>", "name": "<name>", "status": "execute", "progress": "T1/T7" }
  ],
  "inProgressTasks": [
    { "id": "<task-id>", "title": "<title>", "assignedTo": "<orchestrator>", "priority": "medium" }
  ],
  "urgentTodoTasks": [
    { "id": "<task-id>", "title": "<title>" }
  ],
  "blockers": ["<blocker description>"],
  "pendingDecisions": ["<decision description>"],
  "recentCommits": [
    { "hash": "<short-hash>", "msg": "<commit message>" }
  ],
  "summary3Lines": [
    "<Line 1: where we are>",
    "<Line 2: what is blocking or pending>",
    "<Line 3: what to do first post-compact>"
  ]
}
```

**Step 4 — Build briefing note payload**

Schema `session-snapshot-YYYY-MM-DD-HHMM`:

```
topic:        daily
title:        "Session snapshot — <orchestrator> — YYYY-MM-DD HHhMM"
participants: [<orchestrator>, "operator"]
createdBy:    <orchestrator>
content:
  ## Snapshot context
  Memory link : <memId>                    # filled after Step 5 store_memory
  Compaction triggered by : <user|auto>

  ## Active missions (<= 5)
  - <name> (<id>) — <status> — <pilot> — <progress>

  ## In-progress tasks (<= 10)
  - <title> (<id>) — <assignee> — <priority>

  ## Pending decisions (<= 5)
  - <decision> (<context>)

  ## Active blockers
  - <blocker> (since <date>)

  ## 3-line summary for next session
  <line 1>
  <line 2>
  <line 3>
```

**Step 5 — Persist**

```bash
# 1. Store memory (returns <memId>)
mcp__vantage-peers__store_memory \
  namespace="project/<bu>" \
  type="reference" \
  content="<JSON.stringify(payload from Step 3)>" \
  createdBy="<orchestrator>"

# 2. Create briefing note (insert <memId> in Memory link line first)
mcp__vantage-peers__create_briefing_note \
  topic="daily" \
  title="Session snapshot — <orchestrator> — YYYY-MM-DD HHhMM" \
  participants=["<orchestrator>", "operator"] \
  content="<content from Step 4 with <memId> filled>" \
  createdBy="<orchestrator>"
# Returns <briefId>
```

**Step 6 — Output user-facing summary**

Minimal pattern (5 lines, always print):

```
Snapshot saved.
Memory   : <memId>
Briefing : <briefId>
Resume   : recall query="state-of-the-session" namespace="project/<bu>" limit=1
You can compact.
```

Verbose pattern (optional, print in autonomous mode or if >0 blockers):

```
Snapshot saved.
Memory   : <memId>
Briefing : <briefId>

3-line summary :
1. <line 1>
2. <line 2>
3. <line 3>

Resume   : recall query="state-of-the-session" namespace="project/<bu>" limit=1
You can compact.
```

## RULES

- Run BEFORE the operator compacts. This skill is human-triggered (or explicitly called by an autonomous orchestrator pre-compaction). Never auto-trigger on unrelated actions.
- Memory namespace = `project/<bu>` (e.g. `project/elpi-corp` for Pi, `project/vantage-peers` for Sigma).
- Memory type = `reference` (long-term recoverable, not `feedback` or `project`).
- Briefing note topic = `daily` (consistent with daily snapshots — enables `list_briefing_notes` filtering).
- Always include `<memId>` in the briefing note content under "Memory link" (cross-linking the two artefacts).
- Never block on optional fetches. `recentCommits` and `pendingDecisions` are best-effort — empty arrays are valid.
- `summary3Lines` is required and must be 3 lines in plain human language: where we are, what blocks or is pending, what to do first post-compact.
- Never hardcode memory IDs, Convex deploy keys, Clerk secrets, or any environment-specific credentials.

## EXAMPLES

### Human mode (operator-triggered)

```
User:  sauvegarde le contexte avant compaction
Pi:    <runs skill workflow steps 1-5>

Output:
  Snapshot saved.
  Memory   : j576jpk8ynr10s2cs42gd29ar985g87x
  Briefing : js75dwrqdmdngzpnyqefpqaj0h85h7j2
  Resume   : recall query="state-of-the-session" namespace="project/elpi-corp" limit=1
  You can compact.
```

### Sigma VPS — Autonomous mode

```
User:  /pre-compact
Sigma: <runs skill workflow steps 1-5 autonomously>

Output:
  Snapshot saved.
  Memory   : j577abc...
  Briefing : js75def...

  3-line summary :
  1. Sigma working on auto-IRP filter v1.0.1 PR #356.
  2. Blocked on Convex prod schema migration approval.
  3. Resume : start T3 (Playwright e2e) once migration is approved.

  Resume   : recall query="state-of-the-session" namespace="project/vantage-peers" limit=1
  Standby.
```

## When Things Go Wrong

| Error scenario | Likely cause | Fix |
|----------------|--------------|-----|
| `store_memory` fails with schema validation error | Content is not a valid JSON string or exceeds size limit | Ensure `JSON.stringify(payload)` produces valid JSON; reduce optional arrays if content is very large |
| `create_briefing_note` succeeds but memory link is empty | `memId` was not inserted before calling create_briefing_note | Always store memory first (Step 5.1), capture the returned ID, insert it into content, then call create_briefing_note (Step 5.2) |
| Post-compact `recall` returns no results | Wrong namespace or query used at resume | Use exactly `recall query="state-of-the-session" namespace="project/<bu>" limit=1` printed in the snapshot output |

## Sellable As

Part of `vantage-peers` plugin v1.0.0. Available via `/plugin install vantage-peers` after deploying VantagePeers MCP server (Railway template or Convex self-host).
