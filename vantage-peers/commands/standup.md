---
description: Generate a daily standup report and file it as a VantagePeers briefing note
allowed-tools:
  - mcp__vantage-peers__list_tasks
  - mcp__vantage-peers__create_briefing_note
  - mcp__vantage-peers__send_message
  - Bash
  - Read
---

Run the `standup` skill: fetch all tasks, get git state, build a structured standup report (DONE / IN PROGRESS / BLOCKERS / GIT), file it as a briefing note in VantagePeers, and optionally ping your team coordinator.
