# vantage-peers plugin

Plug-and-play VantagePeers toolkit — skills + hooks + commands + expert agent for any Claude Code workspace consuming a VantagePeers MCP server. Companion to `vantage-peers-mcp` npm v2.4.x.

Install once, connect to a VantagePeers MCP server, and every Claude Code orchestrator in your workspace gains full VP fluency: messaging, memory, tasks, missions, diary, standup, and session management — all out of the box.

---

## Prerequisites

- A deployed VantagePeers MCP server (Railway one-click at [vantagepeers.com/railway](https://vantagepeers.com/railway) or Convex self-host)
- Claude Code with plugins support
- Your deployment URL and bearer secret

### Claude.ai web also supported

VantagePeers supports Claude.ai web natively via OAuth 2.1 Dynamic Client Registration. Once your Railway MCP server is running, go to claude.ai → Settings → Integrations → Custom MCP servers, paste your Railway URL, and authorize. No bearer token or plugin install required. Full instructions at [vantagepeers.com/docs](https://vantagepeers.com/docs).

---

## Install

```
claude plugin install vantage-peers
```

---

## Quick start (5 minutes)

**Step 1 — Deploy MCP server**

Deploy to Railway: [vantagepeers.com/railway](https://vantagepeers.com/railway). Note your URL (e.g. `https://vantage-peers-abc123.railway.app`) and `BEARER_SECRET`.

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

Append `templates/CLAUDE.md.append` to the bottom of your workspace `CLAUDE.md`. This installs the VantagePeers workflow protocols (recall-before-assumptions, task protocol, namespace conventions).

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

## Skills (9)

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| `/vantage-peers-init` | "verify VP setup", "VP smoke test", "init vantage-peers" | Verifies MCP registration, tests `/health`, smoke-tests auth via `recall`. PASS/FAIL report with fixes. |
| `/check-messages` | "check messages", "any messages", "inbox", "peers" | Polls unread messages, marks read, auto-picks next task (autonomous) or displays (human). |
| `/check-tasks` | "my tasks", "task list", "what should I work on", "backlog" | Fetches all assigned tasks, filters done, sorts by priority, flags blocked tasks. |
| `/daily-start` | "start the day", "morning plan", "daily planning", "session start" | Loads VP context, presents plan for operator (human) or auto-picks highest-priority task (autonomous). |
| `/close-day` | "close day", "end of day", "wrap up", "close session" | Updates task statuses, writes diary, stores session summary, calls `set_summary` to closed. |
| `/pre-compact` | "save context", "before compaction", "snapshot session" | Saves full session state (missions + tasks + blockers + 3-line summary) as memory + briefing note. |
| `/recall` | "recall", "search memory", "what do we know about", "look up" | Semantic + BM25 hybrid search across VP memories. Auto-detects namespace from query. |
| `/standup` | "standup", "status report", "daily report", "sitrep" | Generates structured standup (DONE / IN PROGRESS / BLOCKERS / GIT) + files briefing note. |
| `/write-diary` | "write diary", "diary entry", "log today", "journal entry" | Asks one question then writes a structured diary entry with highlights + blockers. |

---

## Commands (8 slash commands)

| Command | What it does |
|---------|-------------|
| `/check-messages` | Poll inbox + auto-pick next task |
| `/check-tasks` | List your task queue |
| `/close-day` | EOD wrap routine |
| `/daily-start` | Morning session start |
| `/pre-compact` | Snapshot before compaction |
| `/recall <query>` | Search memories |
| `/standup` | File standup report |
| `/vantage-peers-init` | Verify setup |
| `/write-diary` | Write diary entry |

---

## Hooks (5)

| Hook | What it enforces |
|------|-----------------|
| `enforce-evidence-bound-completion` | Every task closure must cite verifiable proof (URL, commit SHA, PR#, test ratio, file path) |
| `enforce-no-task-in-message` | Inter-orchestrator messages with imperative instructions must reference a task ID |
| `enforce-task-quality` | Every new task must include VERIFICATION and TESTS sections in its description |
| `block-time-estimates` | Effort/duration estimates in content are blocked — use TBD or omit |
| `auto-compact-reminder` | Reminds to compact at 35 tool calls, then every 15 |

---

## Agent

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `vantage-peers-expert` | "store this", "recall X", "create task", "set up VP", "what's in memory", "VP namespace", "fix pattern" | Full VP MCP specialist. Knows all ~82 tools, namespace conventions, memory types, T-VERIFY doctrine. |

---

## Templates

| Template | Use |
|----------|-----|
| `CLAUDE.md.append` | Append to workspace CLAUDE.md to install VP workflow protocols |
| `.mcp.json.template` | Copy and fill in URL + bearer secret for MCP registration |

---

## Links

- VantagePeers docs: [vantagepeers.com/docs](https://vantagepeers.com/docs)
- Toolkit reference: [vantagepeers.com/docs/toolkit](https://vantagepeers.com/docs/toolkit)
- Railway deploy: [vantagepeers.com/railway](https://vantagepeers.com/railway)
- Plugin source: [github.com/vantageos-agency/vantage-peers-plugin](https://github.com/vantageos-agency/vantage-peers-plugin)
- VantageOS: [vantageos.agency](https://vantageos.agency)

---

Built by [vantageos-agency](https://vantageos.agency). Part of the VantagePeers ecosystem.
