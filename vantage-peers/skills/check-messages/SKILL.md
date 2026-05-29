---
name: check-messages
description: >
  Check and respond to peer messages from other orchestrators, and (in autonomous mode) also list + pick the next unblocked todo task. In human mode, additionally pull completed dispatched tasks so awareness never depends on an orchestrator remembering to push.
  Use this skill whenever the user says "check messages", "read messages",
  "any messages", "peers", "inbox", "new messages" --
  even if they don't say "check-messages" explicitly.
metadata:
  version: "5.0.0"
  user-invocable: true
---

Check for unread messages in VantagePeers, pull completed dispatched tasks (human mode only), and (in autonomous mode) auto-pick the next todo task.

V5 PRINCIPLE 1 — READ ≠ MARK READ: this skill READS and DISPLAYS messages only. It NEVER calls `mark_as_read` from inside the read step. `mark_as_read` is an EXPLICIT action the orchestrator (or human) takes AFTER processing — when they have decided what to do (act, respond, ignore).

V5 PRINCIPLE 2 — PULL > PUSH (human mode only): orchestrators sometimes finish dispatched work and forget to `send_message`. In human mode, awareness MUST NOT depend on that push. After messages, pull completed dispatched tasks directly. The push is a bonus; the pull is the source of truth.

## WORKFLOW

**Step 1 — Detect mode (human vs autonomous)**

Check orchestrator identity:
- Read the first 20 lines of `CLAUDE.md` in the current workspace (if available).
- If CLAUDE.md header says you are a human-facing orchestrator (interactive session) → **HUMAN MODE**.
- Else (any autonomous orchestrator on VPS or background session) → **AUTONOMOUS MODE**.
- If in doubt, default to autonomous mode.

**Step 2 — Read + display messages (no side effects)**

1. Detect your orchestrator role and instanceId from CLAUDE.md / hostname.
2. Call `mcp__vantage-peers__check_messages` with recipient={role}, recipientInstanceId={instance}.
3. If no messages: continue to Step 3 (human) or Step 5 (autonomous), or say "No new messages".
4. If messages exist:
   - Display each message: `[from] ({fromInstanceId}): {content}`
   - DO NOT call `mark_as_read` from inside this skill.
   - For each message that requires a response, respond via `mcp__vantage-peers__send_message`.
   - If a message contains task instructions for you, it should already exist as a VantagePeers task (the emitter is responsible for creating tasks). Do not duplicate.

**Step 3 — Pull completed dispatched tasks (HUMAN MODE only)**

(Skip in autonomous mode.)

After reading messages, pull completions directly:

1. Call `mcp__vantage-peers__list_tasks` with `createdBy=<your role>`, `status="review"`. Then again with `createdBy=<your role>`, `status="done"`.
2. Keep only tasks completed since the previous check cycle (recent `completedAt`, fallback `updatedAt`).
3. Exclude any already surfaced earlier in this session (dedup by taskId).
4. For each remaining one, display: `[completed] <title> — <assignedTo> — <completionNote>`.
5. Act on the result (merge PR, dispatch next step, close the loop).

**Step 4 — Process + mark_as_read (explicit, post-decision)**

After you have READ the messages (Step 2) and decided what to do with each, call `mcp__vantage-peers__mark_as_read` with the receiptIds of every message you have finished processing.

This applies to BOTH human and autonomous modes. The marking is an action you take as the orchestrator, not a side effect of fetching.

**Step 5 — Autonomous mode: auto-pick + execute next task**

(Skip this step in human mode.)

After processing messages and marking them read:

1. Call `mcp__vantage-peers__list_tasks` with:
   - `assignedTo=<your role>`
   - `status=todo`
   - No limit (or 50)
2. Also call `list_tasks` with `status=in_progress` and `assignedTo=<role>`. For each task actually done but not closed, call `complete_task` with completionNote (stale task cleanup).
3. From the todo list, sort by `priority` (urgent > high > medium > low) then by `_creationTime` (oldest first). Pick the FIRST task whose dependencies (`dependsOn`) are all `status=done` (or whose `dependsOn` is empty).
4. Call `start_task` with that taskId.
5. Execute the task per its description/brief/VERIFICATION/TESTS blocks.
6. On completion: `complete_task` with a detailed completionNote (evidence-bound — cite URL / commit SHA / PR# / VP id / test ratio / counted artifact / file path) + re-invoke this skill to chain to the next.

**Step 6 — Fallback if no todo task**

If the todo queue is empty (or all candidates are blocked):
1. Produce a 3-line standby summary (role, instance, "queue empty, awaiting dispatch" or "blocked on: [list of dependencies]").
2. Do NOT ask for next steps. Do NOT invent work.
3. Exit silently. The next message trigger will re-fire and detect new work.

## RULES

- This skill is READ-ONLY on the messages table at Step 2. It NEVER calls `mark_as_read` inside the read step.
- `mark_as_read` is an EXPLICIT orchestrator action taken AFTER processing a message (Step 4) — not a side effect of reading.
- Respond immediately to any message that asks a question or requests action.
- In autonomous mode: NEVER produce output asking what to do next. Pick a task or standby. Run Step 5 every cycle.
- In human mode: display messages, run Step 3 pull, respond if needed, mark_as_read after processing.
- Never duplicate tasks from message content (emitter owns task creation).
- Evidence-Bound Done doctrine applies: every `complete_task` / `update_task→review|done` must carry a verifiable proof token.
