# MCP server development — DEPRECATED reference

> Migrated 2026-04-20 to dedicated skill.

**→ For all MCP server work, invoke: `Skill mcp-dev`**

Canonical location: `~/.claude/skills/mcp-dev/`

Reference files:

- `~/.claude/skills/mcp-dev/references/scope-and-repos.md` — 12 repos canonical list
- `~/.claude/skills/mcp-dev/references/mode-matrix.md` — 7 servers × modes
- `~/.claude/skills/mcp-dev/references/tool-layout.md` — N+2 standard + Python/TS templates
- `~/.claude/skills/mcp-dev/references/config-parity.md` — category parity rules
- `~/.claude/skills/mcp-dev/references/relay-flow.md` — local ≡ remote UI parity
- `~/.claude/skills/mcp-dev/references/reuse-mcp-core.md` — primitives to reuse
- `~/.claude/skills/mcp-dev/references/audit-commands.md` — gh CLI commands (--limit 1000)
- `~/.claude/skills/mcp-dev/references/backlog-allowlist.md` — auto + explicit allowlist
- `~/.claude/skills/mcp-dev/references/backlog-clearance.md` — priority + per-PR review
- `~/.claude/skills/mcp-dev/references/clean-state.md` — per-server clean paths
- `~/.claude/skills/mcp-dev/references/e2e-full-matrix.md` — 24 configs + 9-step procedure
- `~/.claude/skills/mcp-dev/references/release-cascade.md` — PSR dispatch order
- `~/.claude/skills/mcp-dev/references/non-mcp-repos.md` — qwen3-embed/web-core/plugins/profile checks

**Reason for split:** MCP server development is a standalone domain with 12 active repos, distinct workflows (backlog clearance, full-matrix E2E, release cascade), and frequent session triggers. Keeping it inline in `fullstack-dev` diluted both skills. See memory `feedback_mcp_dev_skill.md` for consolidation context + `~/projects/.superpower/n24q02m/specs/2026-04-20-mcp-dev-skill-design.md` for design rationale.
