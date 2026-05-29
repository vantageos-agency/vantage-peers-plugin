# vantage-peers-plugin

Official Claude Code plugin for [VantagePeers](https://vantagepeers.com) — the persistent memory and multi-orchestrator coordination MCP server for agent swarms.

This repo is the distribution package for VantagePeers clients. It contains the `vantage-peers` plugin (v2.4.0) with everything needed to make any Claude Code workspace VP-fluent immediately: expert agent, 9 autonomous skills, 9 slash commands, 7 quality-enforcement hooks, CLAUDE.md protocol template, and .mcp.json config template.

---

## Prerequisites

- A deployed VantagePeers MCP server. Two options:
  - **Railway one-click** — deploy template at [vantagepeers.com/railway](https://vantagepeers.com/railway) (~3 minutes)
  - **Convex self-host** — follow the [VantagePeers docs](https://vantagepeers.com/docs)
- Claude Code with plugins support

---

## Install

```
claude plugin install vantage-peers
```

### Option B — Manual clone

```bash
git clone https://github.com/vantageos-agency/vantage-peers-plugin.git
cp -r vantage-peers-plugin/vantage-peers ~/.claude/plugins/
```

---

## What's included (v2.4.0)

### Skills (9)

| Skill | Trigger phrases | Purpose |
|-------|----------------|---------|
| `check-messages` | "check messages", "inbox", "any messages", "peers" | Poll unread messages, mark read, auto-pick next task (autonomous) |
| `check-tasks` | "my tasks", "task list", "what should I work on", "backlog" | List all assigned tasks sorted by priority with dependency awareness |
| `close-day` | "close day", "end of day", "wrap up", "close session" | Update tasks, write diary, store session summary, set summary to closed |
| `daily-start` | "start the day", "morning plan", "daily planning", "session start" | Load VP context, present plan (human) or auto-pick first task (autonomous) |
| `pre-compact` | "save context", "before compaction", "snapshot session" | Save full session state as memory + briefing note before compaction |
| `recall` | "recall", "remember", "search memory", "what do we know about" | Semantic + BM25 hybrid search across VP memories |
| `standup` | "standup", "status report", "daily report", "sitrep" | Generate structured standup report and file as briefing note |
| `vantage-peers-init` | "verify VP setup", "VP smoke test", "init vantage-peers" | Smoke-test MCP registration, connectivity, and auth |
| `write-diary` | "write diary", "diary entry", "log today", "journal entry" | Write a structured diary entry to VantagePeers |

### Commands (9 slash commands)

| Command | What it does |
|---------|-------------|
| `/check-messages` | Poll inbox + auto-pick next task |
| `/check-tasks` | List your task queue |
| `/close-day` | EOD wrap routine |
| `/daily-start` | Morning session start |
| `/pre-compact` | Snapshot before compaction |
| `/recall` | Search memories |
| `/standup` | File standup report |
| `/vantage-peers-init` | Verify setup |
| `/write-diary` | Write diary entry |

### Hooks (7 quality-enforcement hooks)

| Hook | Trigger | Effect |
|------|---------|--------|
| `enforce-evidence-bound-completion` | `complete_task`, `update_task` (→review/done) | Blocks task closure without a verifiable proof token (URL, SHA, PR#, count) |
| `enforce-no-task-in-message` | `send_message` | Blocks messages with imperative instructions that have no task reference |
| `enforce-task-quality` | `create_task` | Blocks task creation without VERIFICATION and TESTS sections |
| `block-time-estimates` | Edit, Write, VP tool calls | Blocks effort/duration estimates in content |
| `auto-compact-reminder` | Every tool call | Reminds to compact after 35 tool calls, then every 15 |
| `enforce-mission-template` | `create_mission` | Blocks mission creation without a Mission Template reference (`templateId`) |
| `enforce-brief-template` | `Task` (subagent dispatch) | Blocks subagent briefs without a `Template reference:` line — keeps delegated work structured |

### Agent

| Agent | Purpose |
|-------|---------|
| `vantage-peers-expert` | Full VP MCP specialist — all ~82 tools, namespace conventions, memory types, T-VERIFY doctrine |

### Templates

| Template | Use |
|----------|-----|
| `templates/CLAUDE.md.append` | Append to workspace CLAUDE.md to install VP workflow protocols |
| `templates/.mcp.json.template` | Copy and fill URL + bearer secret for MCP registration |

---

## Quick start

**Step 1 — Deploy MCP server**

Deploy to Railway using the one-click template at [vantagepeers.com/railway](https://vantagepeers.com/railway). Note your deployment URL and `BEARER_SECRET`.

**Step 2 — Configure .mcp.json**

Copy `templates/.mcp.json.template` to `.mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "vantage-peers": {
      "type": "http",
      "url": "https://your-deployment.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer your-bearer-secret"
      }
    }
  }
}
```

Restart Claude Code after saving.

**Step 3 — Append CLAUDE.md template**

Append `templates/CLAUDE.md.append` to the bottom of your workspace `CLAUDE.md`.

**Step 4 — Run init**

```
/vantage-peers-init
```

All 3 checks (registration, connectivity, auth) must show PASS.

**Step 5 — First commands**

```
/check-messages
/check-tasks
/daily-start
```

---

## Links

- VantagePeers docs: [vantagepeers.com/docs](https://vantagepeers.com/docs)
- Toolkit reference: [vantagepeers.com/docs/toolkit](https://vantagepeers.com/docs/toolkit)
- Railway deploy: [vantagepeers.com/railway](https://vantagepeers.com/railway)
- VantageOS agency: [vantageos.agency](https://vantageos.agency)

---

Published by [vantageos-agency](https://github.com/vantageos-agency). Companion to `vantage-peers-mcp` npm v2.4.x.
