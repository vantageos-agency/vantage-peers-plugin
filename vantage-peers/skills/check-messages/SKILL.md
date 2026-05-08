---
name: check-messages
description: >
  Check and respond to peer messages from other orchestrators, and (in autonomous mode) also list + pick the next unblocked todo task.
  Use this skill whenever the user says "check messages", "read messages",
  "any messages", "peers", "inbox", "new messages" --
  even if they don't say "check-messages" explicitly.
allowed-tools: mcp__vantage-peers__* Bash Read
metadata:
  version: "2.0.0"
  user-invocable: true
license: Proprietary
---

Check for unread messages in VantagePeers and, if running autonomously, auto-pick the next todo task.

## TL;DR

Polls VantagePeers for unread messages, displays and marks them read, then (in autonomous mode) picks and starts the next unblocked todo task. In human mode, stops after message display.

## Decision Tree

```
What mode is this orchestrator running in?
├── CLAUDE.md header = "You are Pi" AND workspace is the human operator's machine
│   └── HUMAN MODE → Steps 1-2 only (display messages, mark read, respond if needed). Stop. Do NOT auto-pick tasks.
└── Any other orchestrator or workspace (VPS, autonomous agent, etc.)
    └── AUTONOMOUS MODE → Steps 1-2 (messages) then Step 3 (auto-pick next task).
        ├── Todo queue has unblocked tasks → pick highest-priority, start_task, execute, complete_task, loop
        └── Queue empty or all blocked → 3-line standby summary, exit silently
```

## WORKFLOW

**Step 1 — Detect mode (human vs autonomous)**

Check orchestrator identity:
- Read the first 20 lines of `CLAUDE.md` in the current workspace (if available).
- If CLAUDE.md header says "You are Pi" AND the workspace is clearly a human operator's interactive machine (not a VPS/server) → **HUMAN MODE**.
- Else (any VPS orchestrator: sigma, alpha, lambda, victor, tau, phi, omega, eta, zeta, proxima, verify, scan, etc.) → **AUTONOMOUS MODE**.
- If in doubt, default to autonomous mode.

**Step 2 — Check messages**

1. Detect your orchestrator role and instanceId from CLAUDE.md / hostname.
2. Call `mcp__vantage-peers__check_messages` with recipient={role}, recipientInstanceId={instance}.
3. If no messages: continue to Step 3 (autonomous) or say "No new messages" (human).
4. If messages exist:
   - Display each message: `[from] ({fromInstanceId}): {content}`
   - Call `mcp__vantage-peers__mark_as_read` with all receiptIds.
   - For each message that requires a response, respond via `mcp__vantage-peers__send_message`.
   - If a message contains task instructions for you, it should already exist as a VantagePeers task (the emitter is responsible for creating tasks — do not duplicate).

**Step 3 — Autonomous mode: auto-pick + execute next task**

(Skip this step in human mode.)

After processing messages:

1. Call `mcp__vantage-peers__list_tasks` with:
   - `assignedTo=<your role>`
   - `status=todo`
   - No limit (or 50)
2. Also call `list_tasks` with `status=in_progress` and `assignedTo=<role>`. For each task actually done but not closed, call `complete_task` with completionNote (stale task cleanup).
3. From the todo list, sort by `priority` (urgent > high > medium > low) then by `_creationTime` (oldest first). Pick the FIRST task whose dependencies (`dependsOn`) are all `status=done` (or whose `dependsOn` is empty).
4. Call `start_task` with that taskId.
5. Execute the task per its description/brief/VERIFICATION/TESTS blocks.
6. On completion: `complete_task` with a detailed completionNote + re-invoke this skill (`/check-messages`) to chain to the next.

**Step 4 — Fallback if no todo task**

If the todo queue is empty (or all blocked on dependencies):
1. Produce a 3-line standby summary (role, instance, "queue empty, awaiting dispatch" or "blocked on: [list of dependencies]").
2. Do NOT ask the operator for next steps. Do NOT invent work.
3. Exit silently. The cron `check_messages every 5 minutes` (or next message trigger) will re-fire and detect new work.

## RULES

- Always mark messages as read after displaying them.
- Respond immediately to any message that asks a question or requests action.
- In autonomous mode: NEVER produce output asking the operator what to do next. Pick a task or standby.
- In human mode: display messages, mark read, respond if needed. Do NOT auto-pick tasks.
- Never duplicate tasks from message content (the emitter owns task creation per the standard task protocol — see VantagePeers docs).

## When Things Go Wrong

| Error scenario | Likely cause | Fix |
|----------------|--------------|-----|
| `check_messages` returns auth error or timeout | MCP server unreachable or bearer token mismatch | Run `/vantage-peers-init` to diagnose; verify Railway deployment is running and `BEARER_SECRET` matches `.mcp.json` |
| Task auto-pick loops endlessly on the same task | `complete_task` was not called (or failed silently) before re-invoking | Check that `complete_task` returns success before looping; inspect task status via `list_tasks` |
| All tasks show as blocked on dependencies | Dependency tasks are stuck in `in_progress` or `todo` state | Check dependency tasks with `get_task`; close stale in_progress tasks with `complete_task` before re-running |

## Sellable As

Part of `vantage-peers` plugin v1.0.0. Available via `/plugin install vantage-peers` after deploying VantagePeers MCP server (Railway template or Convex self-host).
