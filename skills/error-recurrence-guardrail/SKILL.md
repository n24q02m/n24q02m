---
name: error-recurrence-guardrail
description: Use after any Bash/tool call with non-zero exit, after user correction containing "không/never/sai/đã nói rồi/again wrong", or on /retro. Detects errors (tool failures, test fails, user corrections) recurring M>=2 times, proposes `<important if>` guardrail block for global CLAUDE.md. Parses transcripts for stderr/test-fail/correction patterns, hashes normalized error signatures, increments counter in ~/.claude/error-ledger.jsonl.
when_to_use: after non-zero exit, after user correction with repeat signal, /retro
tools: Read, Bash, Grep, Edit, mcp__plugin_mnemo-mcp__mnemo
threshold_m: 2
ledger_path: ~/.claude/error-ledger.jsonl
version: 0.1.0
---

# error-recurrence-guardrail

## Trigger

1. Non-zero exit of any Bash/tool call → auto-increment ledger
2. User correction message contains recurrence signal: "không", "never", "sai", "đã nói rồi", "again wrong"
3. `/retro` weekly review

## Ledger schema (JSONL, `~/.claude/error-ledger.jsonl`)

Each line:
```json
{
  "ts": "ISO8601",
  "session_id": "uuid",
  "error_signature": "sha256-16",
  "normalized": "short description",
  "root_cause_guess": "string",
  "count": N,
  "sessions": ["s1", "s2"],
  "proposed_rule": "pending|rule-text",
  "status": "pending|promoted|dismissed"
}
```

## Algorithm

1. On trigger, hash error content (normalized: strip paths, timestamps, PIDs, line numbers) → signature
2. Increment `count` for matching signature in ledger (add session to `sessions`)
3. If `count >= threshold_m=2` and `status == "pending"`: generate proposal:

   ```markdown
   <important if="<trigger pattern>">
   - **<RULE NAME>**: <rule>. Evidence: occurred <M> times in sessions <ids>. Rationale: <root cause>. Verify: <test>.
   </important>
   ```

4. Show diff in Vietnamese, wait user y/n
5. If y: append to CLAUDE.md, set `status=promoted`
6. If n: set `status=dismissed`, stop re-surfacing

## Safety

- Pressure test proposed rule via subagent before promoting (per `superpowers:writing-skills` RED-GREEN)
- Never modify CLAUDE.md without user approval
- Respect `superpowers:verification-before-completion`
- Dismissed errors: skip re-prompt for 30 days

## Implementation

See `scripts/error_ledger.py` + `tests/test_error_recurrence_guardrail.py`.
