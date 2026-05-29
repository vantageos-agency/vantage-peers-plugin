---
description: Check unread messages from other orchestrators and auto-pick the next task (autonomous mode)
argument-hint: "[--role <role>]"
allowed-tools:
  - mcp__vantage-peers__check_messages
  - mcp__vantage-peers__send_message
  - mcp__vantage-peers__mark_as_read
  - mcp__vantage-peers__list_tasks
  - mcp__vantage-peers__start_task
  - mcp__vantage-peers__complete_task
---

Run the `check-messages` skill: poll unread VantagePeers messages, respond to any that require action, mark processed messages as read, and (in autonomous mode) auto-pick and start the next unblocked task.

$ARGUMENTS
