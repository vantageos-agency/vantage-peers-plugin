---
name: close-day
description: >
  End-of-day routine: update tasks, write diary, store session summary.
  Use this skill whenever the user says "close day", "end of day",
  "wrap up", "call it a day", "close session", "daily close",
  or mentions ending their work session -- even if they don't say "close-day" explicitly.
allowed-tools: mcp__vantage-peers__* Read Write Bash Glob Grep
metadata:
  version: "1.0.0"
  user-invocable: true
license: Proprietary
---

You are the end-of-day routine. You run once at session end to close out the day cleanly.

## TL;DR

Runs the end-of-day sequence for any orchestrator: updates all task statuses, writes a diary entry, stores a session summary memory, and sets the orchestrator status to "session closed".

## Decision Tree

```
Is there an active session to close?
├── Tasks in in_progress or todo state → Step 2 (update tasks) is required
│   ├── Task completed today → complete_task with completionNote
│   ├── Task partially done → leave as in_progress
│   ├── Task blocked → update_task status=blocked
│   └── Task needs review → update_task status=review
└── No tasks to update → skip to Step 3 (write diary)

Is this human mode or autonomous mode?
├── Human mode → Step 3 asks "Key moments today?" and waits for answer
└── Autonomous mode → Step 3 composes diary from task completions and context (no question asked)
```

## WHAT YOU DO

Four steps, in order:
1. **Update tasks** -- review and update all task statuses in VantagePeers
2. **Write diary** -- store the day's diary entry in VantagePeers
3. **Store session summary** -- save a memory summarizing the session
4. **Close** -- set summary to "session closed"

## WORKFLOW

**Step 1 -- Detect identity (silent)**

Determine who you are:
- Read the workspace CLAUDE.md to find the orchestrator role (e.g., pi, tau, phi)
- Determine instanceId from hostname or CLAUDE.md
- Run `date` to get current date in ISO format (YYYY-MM-DD)

**Step 2 -- Update tasks**

Fetch tasks:
- `mcp__vantage-peers__list_tasks` assignedTo={role}, status="in_progress"
- `mcp__vantage-peers__list_tasks` assignedTo={role}, status="todo"

For each in_progress task:
- If completed today -> `mcp__vantage-peers__complete_task` with completionNote
- If partially done -> leave as in_progress
- If blocked -> `mcp__vantage-peers__update_task` status="blocked"
- If needs review -> `mcp__vantage-peers__update_task` status="review"

Show the user a summary:
```
TASK STATUS UPDATE:
- Completed: X tasks
- In progress: X tasks (carrying to tomorrow)
- Blocked: X tasks
- Review: X tasks
- Todo: X tasks remaining
```

**Step 3 -- Write diary**

Ask the user: "Key moments today?" (ONE question. Wait for answer.)

Then write the diary entry:
- `mcp__vantage-peers__write_diary` with date={today}, orchestrator={role}
- Content: what was done, decisions made, blockers encountered
- highlights: list of key achievements
- blockers: list of blockers (if any)

**Step 4 -- Store session summary**

Store a project memory summarizing the session:
- `mcp__vantage-peers__store_memory` namespace="orchestrator/{role}", type="project"
- Content: 3-5 sentence summary of what happened, what's pending, what's next

**Step 5 -- Close**

Set summary to closed:
- `mcp__vantage-peers__set_summary` orchestratorId={role}, instanceId={instanceId}, summary="Session closed -- {date}"

Say: "Day closed. {X} tasks updated, diary written, summary stored."

## RULES

- Never skip task update. Every in_progress task must be accounted for.
- Diary is mandatory. Even if it's short. Something always happened.
- One question only (Step 3). Don't ask about each task individually.
- The session summary must be useful for the NEXT session startup -- include what's pending and what to start with.
- This skill works for any orchestrator. It auto-detects identity from the workspace.

## When Things Go Wrong

| Error scenario | Likely cause | Fix |
|----------------|--------------|-----|
| `write_diary` fails with validation error | Date format not ISO (YYYY-MM-DD) or orchestrator field missing | Run `date +%Y-%m-%d` to get the correct format; verify orchestrator role is set from CLAUDE.md |
| `set_summary` returns "orchestrator not found" | Profile not registered for this orchestrator | Call `mcp__vantage-peers__register_profile` with orchestratorId and instanceId before calling set_summary |
| `list_tasks` returns empty but tasks exist | `assignedTo` field doesn't match role name exactly | Cross-check the role name in CLAUDE.md vs. the value used when tasks were created; use `list_tasks` without filter to inspect all tasks |

## Sellable As

Part of `vantage-peers` plugin v1.0.0. Available via `/plugin install vantage-peers` after deploying VantagePeers MCP server (Railway template or Convex self-host).
