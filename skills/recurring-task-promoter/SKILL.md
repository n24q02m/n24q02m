---
name: recurring-task-promoter
description: Use when session ends via mnemo-mcp:session-handoff, /retro runs, or user says "again"/"lại"/"every time"/"keep doing". Detects tasks user requested 3+ times across sessions and auto-proposes new skill, workflow, or CLAUDE.md rule. Scans mnemo memory + ~/.claude/projects transcripts, clusters by verb-target, emits promotion proposal with evidence. Never auto-writes — always presents diff for user approval.
when_to_use: end of session, /retro weekly, user expresses recurrence signal
tools: Read, Grep, Glob, Bash, Edit, mcp__plugin_mnemo-mcp__mnemo
threshold_n: 3
version: 0.1.0
---

# recurring-task-promoter

## Trigger

Activate when:
1. `mnemo-mcp:session-handoff` called at session end
2. User invokes `/retro`
3. User message contains recurrence signal: "again", "lại phải", "every time", "keep doing", "vẫn phải"

## Algorithm

1. Scan `~/.claude/projects/*/*.jsonl` for last 30 days
2. Extract action tuples `(verb, target, context)` from user messages using pattern matching
3. Cluster by normalized `(verb, target)` pair — case-insensitive + stem-normalized
4. Report clusters with count >= `threshold_n=3`
5. For each high-count cluster, draft promotion:
   - **Ephemeral task** → new skill in `~/.claude/skills/<slug>/SKILL.md`
   - **Hard rule** → CLAUDE.md bullet or `<important if>` block
   - **Project-specific** → project-level `CLAUDE.md` entry
6. Present diff in Vietnamese, wait for user y/n

## Safety

- Never auto-write — always present diff for approval
- Include evidence table `[session-id, date, quote]` per promotion
- Skip clusters where user already corrected behavior (check mnemo `feedback_*.md`)
- Respect `feedback_verify_subagent_output.md` — verify cluster accuracy before proposing

## Implementation

See `scripts/cluster_tasks.py` for cluster logic + `tests/test_recurring_task_promoter.py` for pressure tests.

## References

- Inspired by Cline "Self-Improving Cline" blog + MindStudio Learnings.md loop
- Integrates with existing `mnemo-mcp:session-handoff` + `claude-md-management:revise-claude-md`
