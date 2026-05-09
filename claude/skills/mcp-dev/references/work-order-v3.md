# Work Order v3 — BACKLOG → BETA → TEST A (T0) → TEST B → STABLE → POST-VERIFY

(Locked 2026-04-30, **updated 2026-05-03 drop T2**, BẤT BIẾN)

Trong session multi-step có fix + release, 6 phase BẮT BUỘC theo thứ tự, KHÔNG skip, KHÔNG đổi order.

## Phase 1 — Clear backlog / feat / fix

PRs=0 + issues=allowlist + dependabot=0 + codeql=0 + secret-scan=0 trên TẤT CẢ 13 repo scope.

Verify qua:
- `gh pr list --limit 1000 --state open`
- `gh issue list --limit 1000`
- `gh api repos/<>/dependabot/alerts`

## Phase 2 — Release BETA

CD dispatch `release_type=beta` cho mcp-core trước, rồi cascade plugins. `:beta` artifacts publish lên PyPI/npm/Docker để Test B install.

## Phase 3 — Test A: T0 ONLY (precommit + CI auto)

`feedback_drop_t2_for_test_b.md` (2026-05-03): T2 driver matrix DROPPED. Code-driven test KHÔNG validate được real CC integration (relay browser flow + plugin.json env block + OAuth/JWT round-trip + transport switch). Test B trong CC cover toàn bộ.

T0 keeps:
- Code-path coverage: transport_check, credential_state, SearXNG runner, stdio handlers
- No upstream identity needed
- Run automatically via precommit hook + CI on every push/PR

KHÔNG chạy `make e2e-full` hoặc bất kỳ T2 driver config nào (email-gmail, telegram-bot, imagine, godot-with-exe, email-outlook, telegram-user, notion-oauth, wet-full, mnemo-full, *-stdio-direct). Re-run T2 = vi phạm `feedback_drop_t2_for_test_b.md`.

## Phase 4 — Test B trên 3 IDE (matrix-in-settings)

`feedback_settings_matrix_skip_plugin.md` (2026-05-03): Test B fixture = 8 plugin × 3 method = 24 entries TRỰC TIẾP trong `~/.claude.json mcpServers`, KHÔNG qua plugin marketplace install (stale cache + version drift + env block reset + /reload-plugins unreliable). 1 CC restart loads tất cả 24.

3 methods per plugin:
- Method 1: stdio uvx (default install equivalent) — `command: uvx, args: [...prerelease=allow, --from, <plugin>==<beta>, <plugin>]`, env: skret creds
- Method 2: HTTP Docker — pre-spin `docker run -p <port>` ghcr image, settings entry `type: http, url: http://localhost:<port>/mcp`
- Method 3: stdio Docker — `command: docker, args: [run, -i, --rm, -e MCP_TRANSPORT, -e <skret>, ghcr.io/n24q02m/<plugin>:<beta>]`, env: skret

Per `real-plugin-verification.md` 4 yêu cầu:
- Step 0: uvx/npx cache version match latest published
- Step 1: `read_config(server_name)` trả secret
- Step 2: ≥1 DOMAIN tool call PER ENTRY qua `mcp__plugin_<plugin>_<server>__<tool>` Claude Code MCP harness, evidence table có input + result excerpt
- Step 3: 1 daemon per server, cleanup stale lock files
- Step 4: single + multi-user mode (qua deployment property)

Clients: Claude Code (mandatory), Cursor/Copilot (user-driven manual).

ToolSearch resolve / httpx probe / `__help` KHÔNG count = sloppy verify.

## Phase 5 — Release STABLE

CHỈ khi Test B 24/24 PASS. CD dispatch `release_type=stable`. mcp-core trước, 8 plugin parallel sau. Verify downstream auto-issues + marketplace sync.

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
