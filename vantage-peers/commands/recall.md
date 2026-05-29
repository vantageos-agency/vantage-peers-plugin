---
description: Search VantagePeers memories by query
argument-hint: "<query> [--namespace <namespace>] [--limit <n>]"
allowed-tools:
  - mcp__vantage-peers__recall
  - mcp__vantage-peers__list_memories
---

Run the `recall` skill: semantic + BM25 hybrid search across VantagePeers memories. Auto-detects the best namespace from your query. Returns formatted results with metadata.

$ARGUMENTS
