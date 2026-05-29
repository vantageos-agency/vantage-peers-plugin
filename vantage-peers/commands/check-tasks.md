---
description: List all tasks assigned to you, sorted by priority with dependency awareness
argument-hint: "[--role <role>]"
allowed-tools:
  - mcp__vantage-peers__list_tasks
  - mcp__vantage-peers__get_task
---

Run the `check-tasks` skill: fetch all tasks assigned to your role, filter out completed tasks, sort by priority (urgent > high > medium > low), and flag any blocked by unmet dependencies.

$ARGUMENTS
