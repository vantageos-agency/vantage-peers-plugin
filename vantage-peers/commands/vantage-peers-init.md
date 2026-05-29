---
description: Verify and smoke-test the VantagePeers MCP setup in the current workspace
allowed-tools:
  - mcp__vantage-peers__recall
  - Bash
  - Read
---

Run the `vantage-peers-init` skill: check MCP registration, test the `/health` endpoint, and smoke-test authentication via `recall`. Outputs a PASS/FAIL report with specific fixes for any failure.
