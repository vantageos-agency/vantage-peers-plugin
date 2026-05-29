---
name: standup
description: >
  Daily standup report -- what was done, what's in progress, blockers, git status.
  Use this skill whenever the user says "standup", "status report", "daily report",
  "what did you do", "progress report", "sitrep", "report", "where are you",
  or asks about current work status -- even if they don't say "standup" explicitly.
user-invocable: true
allowed-tools: Read, Bash(git *), Bash(date)
---

# Standup

Generate a structured standup report and file it as a briefing note in VantagePeers.

## WORKFLOW

1. Detect orchestrator role and instanceId from CLAUDE.md
2. Get current date: `date +%Y-%m-%d`
3. Fetch all tasks: `mcp__vantage-peers__list_tasks` assignedTo={role}
4. Get git state: `git status --short` and `git log --oneline -10`
5. Build the report (see format below)
6. File: `mcp__vantage-peers__create_briefing_note` title="Standup {role} {date}", topic="standup", participants=["{role}"], createdBy="{role}"
7. Optionally ping your team coordinator. Read `STANDUP_CHANNEL` from your workspace `CLAUDE.md` (a single line `STANDUP_CHANNEL: <channel-name>`). If set, call `mcp__vantage-peers__send_message` channel=`<channel-name>`, from="{role}", content="Standup filed -- {summary}". If `STANDUP_CHANNEL` is absent, skip the ping silently — no hardcoded fallback.

## OUTPUT FORMAT

```
STANDUP -- {role} ({instanceId}) -- {date}

DONE (since last standup):
- [task title] -- [completionNote]

IN PROGRESS:
- [task title] -- [status, % estimate]

BLOCKERS:
- [description] -- [what's needed]

GIT:
- Branch: {branch}
- Uncommitted: {count} files
- Ready to push: yes/no
```

## RULES

- DONE = status "done", completedAt within last 24h
- IN PROGRESS = status "in_progress" or "review"
- BLOCKERS = status "blocked" + unmet dependencies
- Git status is mandatory
- If nothing done, say so. No padding.
- The briefing note is the permanent record. The message is just a ping.
- 5 lines beats 50.

## CONFIGURATION (client-facing)

The optional team-coordinator ping (step 7) reads its target from your workspace `CLAUDE.md`. Add a single line:

```
STANDUP_CHANNEL: team-coord
```

Replace `team-coord` with whatever channel name your team uses (e.g. `eng-leads`, `daily-standups`, `you@yourdomain.com` for a direct DM channel). If you omit this line, step 7 is skipped — only the briefing note is filed.

This skill ships with **no hardcoded fallback channel**. The plugin is client-agnostic; configure it for your workspace, not ours.
