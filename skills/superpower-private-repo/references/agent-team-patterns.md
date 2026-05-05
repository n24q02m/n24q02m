# Agent Team Patterns (Proactive)

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` đã bật ở `~/.claude/settings.json` từ trước, Claude Code v2.1.32+ đủ điều kiện. Khi task khớp 1 trong 4 pattern sau, PHẢI đề xuất tạo team 3-5 teammate thay vì chỉ dispatch `Agent` tool subagent.

## 4 patterns

1. **Research & review song song** — 3 reviewer cho 1 PR: security + perf + coverage
2. **Competing hypotheses debug** — nhiều teammate thử các theory khác nhau, challenge lẫn nhau
3. **Cross-layer coordination** — 1 teammate own frontend, 1 own backend, 1 own test, tránh context bleed
4. **Parallel new modules** — vd 4 Studio submode mỗi cái 1 teammate owner

## Khác biệt cốt lõi

- **Teammates**: context window riêng + communicate TRỰC TIẾP nhau qua shared task list + mailbox
- **Subagent**: chỉ report-back qua main

## Constraints

- Windows giới hạn in-process mode (Shift+Down cycle teammates), không có split-pane tmux/iTerm2
- Token cost scale linear theo teammate count → 3-5 teammate sweet spot, ≥6 diminishing return
- Có thể reuse subagent_type (feature-dev:code-architect, code-reviewer, code-explorer) làm teammate type

Memory: `feedback_agent_teams_proactive.md`.
