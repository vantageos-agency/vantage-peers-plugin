---
name: write-diary
description: >
  Write a diary entry in VantagePeers for today. Use this skill whenever the user says
  "write diary", "diary entry", "log today", "journal entry", "daily log",
  "write my diary", "note today", or asks to record what happened today --
  even if they don't say "write-diary" explicitly.
user-invocable: true
allowed-tools: mcp__vantage-peers__*, Bash(date)
---

Write a structured diary entry to VantagePeers for today.

## WORKFLOW

1. Detect orchestrator role from CLAUDE.md
2. Get current date: `date +%Y-%m-%d`
3. Ask the operator ONE question: "What happened today? (key moments, decisions, blockers)"
4. Wait for the answer.
5. Write the diary entry:
   ```
   mcp__vantage-peers__write_diary
     date={today}
     orchestrator={role}
     content={what was done, decisions made, blockers encountered}
     highlights=[list of key achievements]
     blockers=[list of blockers, if any]
   ```
6. Confirm: "Diary entry written for {date}."

## RULES

- ONE question to the operator. Do not ask about each task individually.
- Diary is mandatory. Even if it's short. Something always happened.
- `highlights` should be a list of 2-5 achievements worth remembering.
- `blockers` is optional — leave empty if none.
- Never fabricate diary content — base it strictly on what the operator tells you.
- If writing as part of close-day, skip Step 3 (the operator already provided context).
