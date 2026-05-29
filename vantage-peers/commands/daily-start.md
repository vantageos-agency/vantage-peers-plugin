---
description: Run the morning session-start routine — load VP context and plan or auto-pick today's first task
allowed-tools:
  - mcp__vantage-peers__recall
  - mcp__vantage-peers__list_memories
  - mcp__vantage-peers__list_tasks
  - mcp__vantage-peers__start_task
  - Read
  - Bash
---

Run the `daily-start` skill: load VantagePeers context (memories + tasks + missions), detect human vs autonomous mode, and either present a prioritized plan for operator confirmation (human mode) or silently pick and start the highest-priority unblocked task (autonomous mode).
