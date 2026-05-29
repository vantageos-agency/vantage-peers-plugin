#!/usr/bin/env python3
"""
PreToolUse hook : block time estimates in task/mission/message content.

Blocks tool calls (Edit, Write, send_message, create_task, update_task,
create_mission) whose payload contains effort/duration estimates
(e.g., "1-2 days", "Estimated: 30min", "~5h", "2h dev").

Reason: Effort estimates made without data erode trust and are structurally
prevented to enforce evidence-based workflows.

Override: prefix the line with `// allow-time-estimate: <reason>` for
legitimate timing config (cron schedule, polling interval, animation
duration, etc.) — not effort estimates.
"""

import json
import re
import sys

# Patterns that match effort/duration estimates
FORBIDDEN_PATTERNS = [
    # "Estimated: 1h", "Estimated 30 min", "Estimated 1-2 jours"
    r"(?i)estimated?\s*:?\s*[~\d]",
    # "1-2 jours", "1-2 heures", "30-45 min"
    r"\b\d+\s*[-à]\s*\d+\s*(jour|jours|heure|heures|h|min|mn|mins|minutes|heures?|hours?)\b",
    # "~1 min", "~5h", "~2 jours", "~30 min"
    r"~\s*\d+\s*\.?\d*\s*(min|mn|mins|minute|minutes|h|hour|hours|jour|jours|heure|heures|day|days)\b",
    # "1h max", "2 jours max", "30min max"
    r"\b\d+\s*\.?\d*\s*(min|mn|h|jour|jours|heure|heures|hour|hours|day|days)\s*(max|env|environ|approx|approximately|\.)",
    # "ETA 30min", "ETA 2h"
    r"(?i)\beta\s*:?\s*\d",
    # "5-10 min de revue", "30 minutes de dev"
    r"\b\d+\s*\.?\d*\s*(?:min|mn|h|jour|jours|heure|heures|hour|hours|day|days)\s+de\s+(dev|revue|review|test|debug|coding|recherche|research|investigation|setup|implem|impl|implementation|impl\.)",
    # "## Estimated\n2h" or similar markdown sections
    r"(?im)^#+\s*estimated?\s*$",
    # Explicit time effort phrasings
    r"(?i)\b(?:effort|temps|time|durée|duration)\s*(?:estimé?|estimated?|prévu?|expected?)\s*:?\s*[~\d]",
]

OVERRIDE_PATTERN = re.compile(r"//\s*allow-time-estimate:", re.IGNORECASE)


def extract_text_from_input(tool_name: str, tool_input: dict) -> str:
    """Aggregate all string fields that could carry an estimate."""
    parts = []
    if tool_name in ("Edit", "MultiEdit"):
        parts.append(tool_input.get("new_string", ""))
        parts.append(tool_input.get("old_string", ""))
    elif tool_name == "Write":
        parts.append(tool_input.get("content", ""))
    elif tool_name in (
        "mcp__vantage-peers__send_message",
        "mcp__vantage-peers__create_task",
        "mcp__vantage-peers__update_task",
        "mcp__vantage-peers__create_mission",
        "mcp__vantage-peers__update_mission",
        "mcp__vantage-peers__create_briefing_note",
        "mcp__vantage-peers__store_memory",
        "mcp__vantage-peers__write_diary",
    ):
        # Fields that may contain prose
        for key in (
            "content", "description", "brief", "completionNote",
            "title", "name", "summary", "body",
        ):
            v = tool_input.get(key)
            if isinstance(v, str):
                parts.append(v)
    return "\n".join(parts)


def find_violations(text: str) -> list[str]:
    """Return list of offending lines (after stripping override-tagged lines)."""
    if not text:
        return []
    violations = []
    for line_idx, line in enumerate(text.splitlines(), start=1):
        if OVERRIDE_PATTERN.search(line):
            continue  # explicit override
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, line):
                violations.append(f"line {line_idx}: {line.strip()[:140]}")
                break
    return violations


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # malformed input — fail open

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    text = extract_text_from_input(tool_name, tool_input)
    violations = find_violations(text)

    if not violations:
        sys.exit(0)  # clean

    # Block
    msg = (
        "BLOCKED: time/effort estimate detected in tool input.\n"
        "\n"
        "Orchestrators are FORBIDDEN from producing effort/duration estimates "
        "(e.g., 'Estimated 1-2 days', '~30 min', '2h max', '5-10 min de revue').\n"
        "Reason: estimates not grounded in data erode trust and lead to poor decisions.\n"
        "\n"
        "Offending lines:\n"
    )
    for v in violations[:5]:  # cap for readability
        msg += f"  - {v}\n"
    if len(violations) > 5:
        msg += f"  ... and {len(violations) - 5} more.\n"
    msg += (
        "\n"
        "Fix: remove the estimate. Use 'TBD' or omit.\n"
        "Override (rare, only for legit timing config — cron, polling, animation): "
        "add comment `// allow-time-estimate: <reason>` on the same line.\n"
    )

    print(msg, file=sys.stderr)
    sys.exit(2)  # exit code 2 = block in Claude Code hook protocol


if __name__ == "__main__":
    main()
