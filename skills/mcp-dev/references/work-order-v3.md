# Work Order v3 — BACKLOG → BETA → E2E → TEST B → STABLE → POST-VERIFY

(Locked 2026-04-30, BẤT BIẾN)

Trong session multi-step có fix + release, 6 phase BẮT BUỘC theo thứ tự, KHÔNG skip, KHÔNG đổi order.

## Phase 1 — Clear backlog / feat / fix

PRs=0 + issues=allowlist + dependabot=0 + codeql=0 + secret-scan=0 trên TẤT CẢ 13 repo scope.

Verify qua:
- `gh pr list --limit 1000 --state open`
- `gh issue list --limit 1000`
- `gh api repos/<>/dependabot/alerts`

## Phase 2 — Release BETA

CD dispatch `release_type=beta` cho mcp-core trước, rồi cascade plugins. `:beta` artifacts publish lên PyPI/npm/Docker để E2E pin và Test B install.

## Phase 3 — E2E full matrix với :beta artifacts

Qua `mcp-core/scripts/e2e/driver.py` (KHÔNG ad-hoc Python SDK script).

- T0 (auto CI)
- T2 stdio-direct (`uvx <plugin>==<beta>`)
- T2 HTTP non-interaction
- T2 HTTP interaction

Mọi config PASS trước khi tiếp.

## Phase 4 — Test B trên 3 IDE

Claude Code + VS Code Copilot + Cursor (CC bắt buộc, Cursor/Copilot user manual).

Per `feedback_real_plugin_test_strict.md`: 8 meaningful tool calls với evidence table (tool name + non-trivial input + result text trong transcript). ToolSearch resolve / httpx probe / `__help` KHÔNG count.

## Phase 5 — Release STABLE

CHỈ khi Test B PASS. CD dispatch `release_type=stable`. mcp-core trước, 8 plugin parallel sau. Verify downstream auto-issues + marketplace sync.

## Phase 6 — Post-release verify

User install `:latest` published artifact, re-run Test B sample; verify multi-daemon = 0, plugin.json env field intact.

## Anti-patterns CẤM

- "Phase X feature done → ready for E2E" khi còn open PRs
- "Đã verify N stdio-direct manual qua Python SDK ≈ E2E driver" — KHÔNG, phải qua `e2e.driver`
- "Skip Test B, release STABLE, test sau" — vi phạm 2026-04-29 D18 spam-tabs incident
- "Mix BETA + STABLE dispatch trong cùng phase" — race condition

Vi phạm → broken release + rework cascade.

## Cross-references

- `~/.claude/skills/mcp-dev/references/release-cascade.md` (cascade detail)
- `~/.claude/skills/mcp-dev/references/e2e-full-matrix.md` (E2E driver detail)
- Memory `feedback_work_order_v3_beta_first.md` (replaces v2/v1)
