---
description: Save current session state to VantagePeers before Claude Code compaction
allowed-tools:
  - mcp__vantage-peers__list_missions
  - mcp__vantage-peers__list_tasks
  - mcp__vantage-peers__recall
  - mcp__vantage-peers__store_memory
  - mcp__vantage-peers__create_briefing_note
  - Bash
  - Read
---

Run the `pre-compact` skill: capture active missions, in-progress tasks, blockers, recent commits, and a 3-line summary into a VantagePeers memory + briefing note so any session can resume exactly where it left off after compaction.
