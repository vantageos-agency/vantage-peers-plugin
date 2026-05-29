# Toolkit Classification — vantage-peers v2.4.0

**Audit date:** 2026-05-29 (Day 86)
**Mission task:** k170mmqpx65jmmvzknj5svxgax87nhfj (VOLET B)
**Auditor:** Sigma — VantageOS Team
**Validator gate:** Laurent (per Day 86 doctrine, Laurent tranche public/internal/BU)

The `vantage-peers` Claude Code plugin ships the public subset only. Internal Fleet and BU-specific artefacts stay in their source workspaces. This document is the canonical classification reference for the v2.4.0 release; it is updated whenever the plugin scope changes.

---

## Bucket 1 — PUBLIC (24 artefacts) — shipped in plugin v2.4.0

### Skills (9)

| Name | One-line purpose |
|------|------------------|
| check-messages | Read peer messages from VantagePeers, mark-as-read explicit post-decision. |
| check-tasks | List + pick next pending VP task by assignee + status + priority. |
| close-day | End-of-day routine: update tasks, write diary, store session summary. |
| daily-start | Morning planning: pending tasks + diary review + daily goals. |
| pre-compact | Save session snapshot to VantagePeers before Claude Code compaction. |
| recall | Semantic search over VP memories by namespace + type. |
| standup | Daily standup briefing note + status report to optional team coordinator. |
| vantage-peers-init | Initialize a new workspace with VP MCP wiring, .mcp.json + CLAUDE.md template. |
| write-diary | Write a daily diary entry via VP write_diary tool. |

### Hooks (5)

| Name | Trigger | One-line purpose |
|------|---------|------------------|
| enforce-evidence-bound-completion.py | PreToolUse on complete_task / update_task→review\|done | Blocks claim-words-only completions; requires verifiable proof tokens (URL / commit SHA / PR# / VP id / ratio / artefact). |
| enforce-no-task-in-message.py | PreToolUse on send_message | Blocks task-instruction content sent via messaging; emitter must create a VP task instead. |
| enforce-task-quality.py | PreToolUse on create_task | Requires VERIFICATION + TESTS sections in task descriptions. |
| block-time-estimates.py | PreToolUse on create_task / update_task | Blocks effort-estimate language (hours / days / weeks) in task descriptions. |
| auto-compact-reminder.py | SessionStart / Stop | Reminds user to invoke pre-compact when context window approaches threshold. |

### Slash commands (9)

| Slash | Wraps skill |
|-------|------------|
| /check-messages | check-messages |
| /check-tasks | check-tasks |
| /close-day | close-day |
| /daily-start | daily-start |
| /pre-compact | pre-compact |
| /recall | recall |
| /standup | standup |
| /vantage-peers-init | vantage-peers-init |
| /write-diary | write-diary |

### Agents (1)

| Name | One-line purpose |
|------|------------------|
| vantage-peers-expert.md | Full VantagePeers MCP specialist agent — invokes the right VP tool for any task, plans missions, handles task lifecycle. |

---

## Bucket 2 — INTERNAL Fleet (18 artefacts) — NOT shipped

Fleet orchestration conventions tied to VantageOS Pi/Sigma routing. Would override client conventions or break in non-fleet environments.

### Internal Fleet hooks (17)

| Name | Rationale |
|------|-----------|
| enforce-signature.py | Fleet PR signature format `Orchestrator: <Role> — <Team> \| YYYY-MM-DD`. VantageOS convention. |
| auto-inject-signature.py | Auto-injects fleet signature using `CLAUDE_ORCHESTRATOR_ROLE` env var infrastructure. |
| enforce-iter-message.py | Day 58 fleet pattern: Eta/Chi must ping Pi after iter ship. References `pi-chromebook` + memory ID. |
| qa-breadcrumb.py | Fleet T6 QA step breadcrumb. Tied to IRP template step naming. |
| block-deploy-without-qa.py | Blocks `convex deploy` without qa-breadcrumb. VantageOS Convex deployment gate. |
| enforce-delegation.py | Blocks source edits from orchestrators. Fleet Pi delegation policy. |
| enforce-eta-approval-before-npm-publish.py | Eta review gate for fleet npm publish. VantageRegistry task validation. |
| enforce-pi-authorization-before-prod-deploy.py | Pi authorization before Convex prod deploy. Fleet-specific. |
| enforce-ship-24-7.py | Fleet shipping policy constraint. |
| enforce-decisive-messaging.py | Fleet voice/tone convention. |
| enforce-component-brief.py | Fleet component brief template enforcement. |
| enforce-mission-template.py | Fleet mission creation template. |
| enforce-merge-gate.py | Fleet merge gate convention (Eta APPROVED + Pi GO MERGE override). |
| enforce-irp-sequence.py | IRP cascade Pi pattern. Fleet incident response. |
| irp-breadcrumb.py | IRP breadcrumb for fleet incident response. |
| strip-claude-from-pr.py | Removes Claude Code branding from PRs. Fleet PR hygiene. |
| enforce-brief-template.py | Pi brief template enforcement for subagent dispatch. |

### Internal Fleet skills (1)

| Name | Rationale |
|------|-----------|
| track-external-issue | Fleet-specific: hardcoded `channel=zeta`, `pilot=zeta`, fleet IRP repo-fix-v1 10-step template. Borderline — could be generalized in v2.5.0 if client demand exists. |

---

## Bucket 3 — BU-specific (6 artefacts) — NOT shipped

Hardcoded to specific Business Unit workflows (Chi / Athena / Demeter / Hermes / Theta) or BU code-style policies. Not portable.

### BU hooks (5)

| Name | BU owner | Rationale |
|------|----------|-----------|
| enforce-analysis-flow.py | Pi-coordination analysis BU workflow | BU-specific analysis workflow gate. |
| enforce-analysis-flow-completion.py | Pi-coordination analysis BU workflow | BU analysis completion gate. |
| block-delete-on-prod.py | Theta CRM deployment policy | BU deployment policy. |
| check-file-size.py | BU code style team | BU code style linting (size limits). |
| check-french-diacritics.py | BU i18n team | i18n linting for French content. |

### BU skills (1)

| Name | BU owner | Rationale |
|------|----------|-----------|
| pricing-research | ElPi Corp marketing | French-language, ElPi Corp brand, Firecrawl deep scrape, not standalone for generic clients. |

---

## Totals

| Bucket | Count |
|--------|-------|
| PUBLIC (shipped v2.4.0) | 9 skills + 5 hooks + 9 commands + 1 agent = **24** |
| INTERNAL Fleet (not shipped) | 17 hooks + 1 skill = **18** |
| BU-specific (not shipped) | 5 hooks + 1 skill = **6** |
| Total artefacts audited | **48** |

---

## Borderline items (for Laurent / Pi review)

1. **track-external-issue** (currently INTERNAL) — Hardcoded fleet refs make it fleet-bound. Generalizable in v2.5.0 if client demand surfaces.

2. **enforce-signature / auto-inject-signature** (currently INTERNAL) — VantageOS fleet PR signature convention. Shipping would override client conventions; could expose as opt-in setting if requested.

3. **write-diary** (currently PUBLIC) — Created from scratch as a thin wrapper of VP `write_diary` tool. No source equivalent in vantage-memory workspace.

4. **standup** (currently PUBLIC) — Source skill hardcoded `channel=pi-chromebook`; plugin version generalizes to optional ping. Clients configure their own channel name in CLAUDE.md.

---

## Sanitization audit (PUBLIC artefacts)

Every public artefact was scanned and stripped of fleet-internal references before shipping. Key sanitizations:

| File | What was removed/replaced |
|------|--------------------------|
| skills/check-messages/SKILL.md | Pi Chromebook hardcoded path; internal memory IDs; VantageRegistry canonical-source section; contentHash; Pi-deferred false-positives language. |
| skills/check-tasks/SKILL.md | `pi-vps-vm` / `pi-chromebook` role examples. |
| skills/standup/SKILL.md | Hardcoded `channel=pi-chromebook` in send_message. |
| hooks/block-time-estimates.py | Pi + Chi + other-orchestrators refs; "Laurent has explicitly demanded" language; Day 64 date ref. |
| hooks/enforce-no-task-in-message.py | `pi-chromebook` + `pi-vps` channel exemptions replaced with `broadcast` / `operator`. |
| hooks/enforce-evidence-bound-completion.py | Day 73-76 retrospective narrative; Day 76 label in docstring. |

---

## Validation gate (Day 86 doctrine)

Per Pi 2026-05-29 message jn7dx7sa942jjxemf208yn2rcs87nbe9, the public/internal/BU classification is **Laurent's call**. PR #3 plugin merge + npm publish v2.4.0 are gated on Laurent's ack of these 3 buckets. Any reclassification triggers a re-audit + manifest update + version bump decision.

---

Orchestrator: Sigma — VantageOS Team | 2026-05-29
