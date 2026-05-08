# vantage-peers-plugin

Official Claude Code plugin for [VantagePeers](https://vantagepeers.com) — the persistent memory and multi-orchestrator coordination MCP server for agent swarms.

This repo is a single-plugin marketplace. It contains the `vantage-peers` plugin with everything needed to make any Claude Code workspace VP-fluent immediately: expert agent, 5 autonomous skills, CLAUDE.md protocol template, and .mcp.json config template.

---

## Prerequisites

- A deployed VantagePeers MCP server. Two options:
  - **Railway one-click** — deploy template at [vantagepeers.com/railway](https://vantagepeers.com/railway) (~3 minutes)
  - **Convex self-host** — follow the [VantagePeers docs](https://vantagepeers.com/docs)
- Claude Code with plugins support

---

## Install

### Option A — Marketplace install (recommended)

```
/plugin marketplace add vantageos-agency/vantage-peers-plugin
/plugin install vantage-peers@vantage-peers-plugin
```

### Option B — Manual clone

```bash
git clone https://github.com/vantageos-agency/vantage-peers-plugin.git
cp -r vantage-peers-plugin/vantage-peers ~/.claude/plugins/
```

---

## What's included

| Item | Path | Purpose |
|------|------|---------|
| Expert agent | `vantage-peers/agents/vantage-peers-expert.md` | Full VP MCP specialist — all 82+ tools, namespaces, T-VERIFY doctrine |
| check-messages | `vantage-peers/skills/check-messages/SKILL.md` | Poll unread messages, mark read, auto-route |
| daily-start | `vantage-peers/skills/daily-start/SKILL.md` | Morning session start, load context, pick tasks |
| close-day | `vantage-peers/skills/close-day/SKILL.md` | EOD wrap: update tasks, diary, session summary |
| pre-compact | `vantage-peers/skills/pre-compact/SKILL.md` | Snapshot state before Claude Code compaction |
| vantage-peers-init | `vantage-peers/skills/vantage-peers-init/SKILL.md` | Smoke-test MCP registration, connectivity, auth |
| CLAUDE.md.append | `vantage-peers/templates/CLAUDE.md.append` | VP workflow protocols for workspace CLAUDE.md |
| .mcp.json.template | `vantage-peers/templates/.mcp.json.template` | MCP config template (fill URL + bearer secret) |

---

## Links

- VantagePeers docs: [vantagepeers.com/docs](https://vantagepeers.com/docs)
- Railway deploy: [vantagepeers.com/railway](https://vantagepeers.com/railway)
- VantageOS agency: [vantageos.agency](https://vantageos.agency)

---

Published by [vantageos-agency](https://github.com/vantageos-agency).
