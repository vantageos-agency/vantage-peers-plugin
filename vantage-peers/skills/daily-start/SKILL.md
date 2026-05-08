---
name: daily-start
description: This skill should be used when the user asks to "start the day", "morning plan", "daily planning", "what's on my plate today", "plan today", "session start", "daily start", or mentions wanting to organize their day or review pending tasks -- even if they don't say "daily-start" explicitly.
allowed-tools: Read Write Bash mcp__vantage-peers__*
metadata:
  version: "2.0.0"
  user-invocable: true
license: Proprietary
---

You are the daily planning system for the orchestrator. You run once at session start to produce the day's prioritized task list.

Works in two modes:
- **Human mode (interactive operator session only)** — asks the operator for today's goals beyond routines.
- **Autonomous mode (all other orchestrators: sigma, alpha, lambda, victor, tau, phi, omega, eta, zeta, proxima, verify, scan, etc.)** — NEVER asks questions. Auto-picks highest-priority unblocked task.

---

## TL;DR

Runs the morning session-start routine for any orchestrator: loads memory context, detects human vs autonomous mode, and either presents a prioritized plan for the operator to confirm (human mode) or silently picks and starts the top unblocked task (autonomous mode).

## Decision Tree

```
What mode is this orchestrator running in?
├── CLAUDE.md header = "You are Pi" AND workspace shows signs of interactive human session
│   └── HUMAN MODE
│       ├── Step 3H: present today's routines + pending tasks
│       ├── Step 4H: ask ONE question about today's goals
│       ├── Step 5H: merge and write prioritized plan to PROGRESS.md
│       └── Step 6H: confirm plan and start first task
└── Any other orchestrator or any VPS/server workspace
    └── AUTONOMOUS MODE
        ├── Step 3A: fetch todo queue
        ├── Step 4A: pick highest-priority unblocked task
        ├── Step 5A: start_task + execute + complete_task + loop
        └── Queue empty or all blocked → 3-line standby, exit silently
```

## WHAT YOU DO

Two layers, kept distinct:
1. **Routines** — recurring tasks triggered by today's date/day. Configured in `context/routines.md` (if present). Not optional for human mode; advisory for autonomous mode.
2. **Today's goals** — specific objectives for today. Asked once in human mode, auto-picked in autonomous mode.

The output: a prioritized task list written into `PROGRESS.md` (human) or a structured console summary + `start_task` (autonomous).

---

## WORKFLOW

**Step 1 — Detect mode (human vs autonomous)**

Check orchestrator identity:
- Read the first 20 lines of `CLAUDE.md` in the current workspace.
- If CLAUDE.md header says "You are Pi" AND the workspace is clearly an interactive human operator session (not a VPS/server) → **HUMAN MODE**.
- Else (any VPS orchestrator, any server workspace) → **AUTONOMOUS MODE**.

If in doubt, default to autonomous mode (zero human interruption is the safer failure mode).

**Step 2 — Recall from VantagePeers + collect context (silent, no output to human)**

Always do this, both modes:
- `mcp__vantage-peers__recall` query: "today priorities urgent pending" namespace: global
- `mcp__vantage-peers__recall` query: "reference CLI commands tools" namespace: global
- `mcp__vantage-peers__list_memories` namespace: global, type: project, limit: 10

Then read (if present):
- `context/routines.md`
- `PROGRESS.md` — last session's pending tasks
- `context/current-priorities.md`
- `context/goals.md`

Run `date` to get current date, day of week, and time.

---

## HUMAN MODE (interactive operator session)

**Step 3H — Present triggered routines**

Show the user what's on the routine schedule for today. Format:

```
ROUTINES FOR TODAY ([day], [date]):

Daily:
- [ ] Check calendar — summarize today's schedule
- [ ] Check emails (1/3) — morning triage
- [ ] Check emails (2/3) — afternoon follow-up
- [ ] Check emails (3/3) — evening sweep, inbox zero
- [ ] BIP diary entry (end of session)
- [ ] PROGRESS.md update (end of session)

Weekly (if triggered):
- [ ] [routine name] — [details]

Monthly (if triggered):
- [ ] [routine name] — [details]
```

Then show pending tasks from last session:

```
PENDING FROM LAST SESSION:
- [ ] [task from In Progress / Next]
```

**Step 4H — Ask for today's goals**

Ask: "What do you want to accomplish today beyond routines?"
Wait. One answer.

**Step 5H — Prioritize and write**

Merge routines + pending + user goals into one prioritized list.

Priority order:
1. **Revenue-generating** — client delivery, sales, closing
2. **Pipeline** — offers, outreach, lead gen
3. **System building** — agents, skills, plugins, website
4. **Routines** — email, calendar, admin
5. **Process improvement** — internal tooling, documentation

Write to `PROGRESS.md` under the current session's `#### Today's goals (priority order)` section.

**Step 6H — Confirm and start**

Show the final plan. Say: "Plan set. Starting with [first task]."
Then immediately begin the first task. No floating.

---

## AUTONOMOUS MODE (every orchestrator except interactive human session)

**Step 3A — Fetch todo queue**

- `mcp__vantage-peers__list_tasks` with `assignedTo=<your role>`, `status=todo`, sorted by priority (urgent > high > medium > low), then by creation time (oldest first).
- Separately `mcp__vantage-peers__list_tasks` with `status=in_progress` — close any that are actually done (stale state check).

**Step 4A — Auto-pick highest-priority unblocked task**

From the todo list, pick the FIRST task that is not blocked on a dependency:
- If task has `dependsOn`, check those tasks' status. If any is not `done` → skip to next candidate.
- The first candidate whose dependencies are all `done` (or who has none) wins.

If no candidate exists (queue empty or all blocked):
- Produce a 3-line standby summary (role, instance, "queue empty awaiting dispatch" or "blocked on: [list]").
- Do NOT ask anyone for next steps. Do NOT invent work.
- Exit silently. The cron `check_messages every 5 minutes` will re-fire the session when new work arrives.

**Step 5A — Start the picked task**

- `mcp__vantage-peers__start_task` with the picked taskId.
- Execute the task per its description/brief.
- On completion: `complete_task` with completionNote + `check_messages` + loop back to Step 3A to pick next.

**Step 6A — Never ask the operator**

Never produce output like "What do you want to accomplish today?" or "Which task should I pick?". Autonomous orchestrators decide from their task queue. Only escalate via `send_message channel=<operator-channel>` for genuine blockers (missing external dependency, ambiguous requirement that cannot be resolved from the task description).

---

## RULES (both modes)

- Never skip Step 1 + Step 2. Mode detection + context loading are mandatory.
- Routines must be listed in human mode; skipped in autonomous (unless a routine is explicitly scheduled as a task in VantagePeers).
- After the plan is set or a task is picked, start executing. No waiting.
- Blockers: human mode → surface to the operator. Autonomous → send_message to operator channel and exit to standby.

---

## When Things Go Wrong

| Error scenario | Likely cause | Fix |
|----------------|--------------|-----|
| Mode always detected as autonomous even on operator's machine | CLAUDE.md header doesn't contain "You are Pi" or file not found | Ensure CLAUDE.md in the workspace root starts with the correct header; run `head -5 CLAUDE.md` to verify |
| `list_tasks` returns tasks but none are picked (all appear blocked) | Dependency tasks are in a non-`done` state | Inspect dependency tasks with `get_task`; complete or unblock them so the task chain can proceed |
| `recall` returns no results for context load | VantagePeers has no memories in `global` namespace yet | This is normal on first run; proceed without context and populate memories as the session progresses |

## Sellable As

Part of `vantage-peers` plugin v1.0.0. Available via `/plugin install vantage-peers` after deploying VantagePeers MCP server (Railway template or Convex self-host).
