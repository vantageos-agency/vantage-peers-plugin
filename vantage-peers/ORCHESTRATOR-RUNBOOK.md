# Orchestrator Runbook — VantagePeers Plugin

Every orchestrator using the `vantage-peers` plugin MUST pass this checklist before operating.

---

## IDENTITY

- [ ] CLAUDE.md defines: name, role, instanceId, workspace, projects managed
- [ ] Orchestrator profile registered in VantagePeers (`register_profile`)
- [ ] `set_summary` called at session start with role + instanceId + current status

## PLUGINS

- [ ] vantage-peers plugin installed (`claude plugin install vantage-peers`)
- [ ] Skills available: /vantage-peers-init, /check-messages, /daily-start, /close-day, /pre-compact
- [ ] Run `/vantage-peers-init` — all 3 checks must PASS before operating

## MCP

- [ ] `vantage-peers` MCP registered in `.mcp.json` or `~/.claude.json`
- [ ] URL format: `<RAILWAY_URL>/mcp` (not the base URL)
- [ ] Bearer secret matches `BEARER_SECRET` env var on the server
- [ ] Health check passes: `curl <RAILWAY_URL>/health` returns `{"version":"2.2.0",...}`

## SKILLS — MANDATORY USAGE

- [ ] `/daily-start` at every session open (human or autonomous mode)
- [ ] `/check-messages` before picking tasks (autonomous) or after session start (human)
- [ ] `/pre-compact` before every Claude Code compaction
- [ ] `/close-day` at every session close

## RULES — ENFORCED BY PROTOCOL

1. **Recall before assumptions.** Never state facts about project state without calling `recall` first.
2. **Store after corrections.** Any time the operator says "no" or "actually" — `store_memory` immediately.
3. **Complete tasks with notes.** `complete_task` without `completionNote` is not allowed.
4. **VERIFICATION + TESTS on every task.** No exceptions. Tasks without these blocks are incomplete.
5. **Mark messages as read.** Always call `mark_as_read` after `check_messages`.
6. **Namespace discipline.** `global` for cross-project facts, `project/<slug>` for codebase-specific, `orchestrator/<role>` for personal state.

## VERIFICATION PROCEDURE

Run this before operating in a new workspace:

```
1. /vantage-peers-init                          # All 3 checks PASS?
2. mcp__vantage-peers__recall query="test"      # Returns array (not error)?
3. /check-messages                              # Messages accessible?
4. /daily-start                                 # Task queue loads?
5. mcp__vantage-peers__set_summary orchestratorId=<role> instanceId=<id> summary="online"
```

If ANY check fails, stop and run the corresponding fix from `/vantage-peers-init` report.

## DEPLOYMENT

To set up a new orchestrator with vantage-peers:

1. Deploy VantagePeers MCP server (Railway template or Convex self-host)
2. Install plugin: `claude plugin install vantage-peers`
3. Copy `.mcp.json.template` from `vantage-peers/templates/` → `.mcp.json` in workspace
4. Fill in `<YOUR_RAILWAY_URL>` and `<YOUR_BEARER_SECRET>`
5. Restart Claude Code
6. Append `CLAUDE.md.append` from `vantage-peers/templates/` to workspace `CLAUDE.md`
7. Run `/vantage-peers-init` — must show ALL PASS
8. Run `/daily-start` — first task or standby message confirms full integration

---

Maintained by vantageos-agency. Issues: https://github.com/vantageos-agency/plugins
