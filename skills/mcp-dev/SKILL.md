---
name: mcp-dev
description: Canonical skill for MCP server stack work (13 repos — expanded 2026-04-24 +imagine-mcp). Use when editing/auditing/testing/releasing ANY of mcp-core, 8 MCP servers (better-notion/email/telegram/godot, wet/mnemo/crg/imagine-mcp), qwen3-embed, web-core, claude-plugins, n24q02m profile — OR running multi-repo backlog + E2E + release cascade. Enforces mode matrix, tool layout N+2, config parity, relay flow parity, reuse mcp-core primitives, clean-state E2E, full matrix testing (15 MCP + 4 non-MCP = 19 configs), empty-backlog gate before release, PSR dispatch order, downstream auto-issue verify.
---

# MCP Dev Skill

Canonical workflow for the 13-repo MCP stack. Invoke this BEFORE any edit, audit, test, or release on any listed repo.

## When to invoke

Trigger keywords: "MCP server", "mcp-core", "better-notion", "better-email", "better-telegram", "wet-mcp", "mnemo", "code-review-graph", "godot-mcp", "imagine-mcp", "qwen3-embed", "web-core", "claude-plugins", "13 repos", "release cascade", "backlog clear", "full matrix E2E", "ship MCP stack", "audit all repos", "verify parity".

## Task type detection

**Branch A — single-repo dev/audit:** load `references/mode-matrix.md` + `references/tool-layout.md` + `references/config-parity.md` + `references/relay-flow.md` + `references/reuse-mcp-core.md`.

**Branch B — multi-repo cascade:** follow Phase 0-5 below.

## Flow (release cascade)

```
Phase 0: Backlog audit (references/audit-commands.md)
  |
  v
  EMPTY BACKLOG gate:
    - open PRs = 0
    - open issues subset-of allowlist (references/backlog-allowlist.md)
    - dependabot + codeql + secret-scanning = 0
  |
  v (fail)
Phase 1: Backlog clear (references/backlog-clearance.md) — interactive per-PR
  |
  +---> loop back to Phase 0 re-audit
  |
  v (pass)
Phase 2: Clean state per server (references/clean-state.md)
  |
  v
Phase 3: Test A — MCP PROTOCOL E2E (references/e2e-full-matrix.md) — 19 configs
  SOURCE CODE: `uv run <server>` / `bun run build && node bin/cli.mjs`
  CLIENT: Python MCP SDK (mcp.ClientSession + stdio_client / streamablehttp_client)
  5 configs auto-verified via CI (#15-19 non-MCP); 14 manual configs require user browser fill
  |
  v
  ALL GREEN (19/19)?
  |
  +---> any fail: back to Phase 1
  |
  v
Phase 4: Release dispatch (references/release-cascade.md) — mcp-core -> 8 MCP -> downstream
  |
  v
Phase 5: Verify (auto-issues, PSR version, downstream pin bump PRs)
  |
  v
Phase 6: Test B — CLIENT INTEGRATION (references/client-integration-test.md)
  PUBLISHED ARTIFACT: `uvx <server>` / `npx @n24q02m/<server>` / plugin from marketplace
  CLIENTS: Claude Code CLI (plugin marketplace), VS Code GitHub Copilot (mcp.json)
  Verify plugin install + auth flow + tool invocation from real client context
  |
  v
Done
```

**Test A vs Test B — 2 phases RIÊNG BIỆT (never merge)**:
- Test A = pre-release, source code, em as MCP client (Python SDK). Phase 3.
- Test B = post-release, published artifact, user as client (Claude Code / VS Code). Phase 6.
- Release MUST sit BETWEEN two tests. No published artifact → no plugin to install → cannot do Test B.
- Merging Test A and Test B = anti-pattern (2026-04-21 violation, see `feedback_work_order_fix_test_release.md`).

## Invariants

1. **Scope** = 13 repos default (see `references/scope-and-repos.md`); explicit override required for subset.
2. **EMPTY BACKLOG gate strict** — see `references/backlog-allowlist.md` for allowed exceptions: Renovate Dashboard auto-allowed (1/repo), explicit long-running with review-by date. Security alerts (dependabot/codeql/secret) are strict zero, no allowlist.
3. **Clean state per server before E2E** — no skip, even if "already configured".
4. **Full matrix (19 configs), not default-only.**
5. **Release only at Phase 4** — no mid-session release, no incremental per-repo release.
6. **Phase 5 must verify downstream auto-issue PRs** exist for core releases (mcp-core release triggers tracking issues in all 8 MCP + 3 consumer repos).
7. **Remote mode = per-JWT-sub multi-user enforced** — any server running `remote-relay`/`remote-oauth` mode MUST store credentials keyed by JWT `sub` (or OAuth-provider user id). No silent fallback to single-user `config.enc`. If upstream mcp-core can't yet provide per-session sub, server MUST REFUSE start in remote mode with explicit error. See `feedback_remote_relay_multi_user_enforcement.md`.

## Red flags (STOP immediately)

- "Test chỉ default mode" → violates invariant 4.
- "Already configured, skip clean state" → violates invariant 3 + `feedback_e2e_clean_state_all_servers.md`.
- "Release this repo now while I clean the others" → violates invariant 5 + `feedback_work_order_fix_test_release.md`.
- "Bulk close PRs to reach gate faster" → violates `feedback_pr_review_must_be_real.md` + `feedback_never_bulk_close.md`.
- "Inject env var so E2E can skip relay" → violates `feedback_full_live_test.md`.
- "Guess data store / env var / relay field" → violates `feedback_data_store_no_guessing.md` + see `references/mode-matrix.md` for truth.
- "Let me add a new mode for X" → violates mode matrix fixed set; each server has fixed default + fixed list of supported alternates.
- "Dual codepath — local form AND remote relay URL simultaneously" → user confusion, violates `feedback_relay_mode_ui_parity.md`.
- "Remote-relay với single-user `writeConfig(SERVER_NAME, raw)` + `// TODO: upstream v1.5 will add sub`" → silent credential leak, violates `feedback_remote_relay_multi_user_enforcement.md`. Either impl per-JWT-sub NOW or REFUSE remote mode start.
- "Skip optional field khi test relay" (2026-04-21) → violates `feedback_relay_fill_all_fields.md`. Mọi field kể cả `required: false` PHẢI fill credential thật. Submit-empty không được coi là PASS — chỉ verify fallback branch, bỏ qua validation/priority logic.
- "Browser automation (Playwright/Puppeteer/Selenium) thay user click submit" (2026-04-21) → violates `feedback_relay_fill_all_fields.md`. User-action là real user, automation = mock layer, cũng cấm programmatic POST tới submit endpoint. Nếu user không có sẵn → pause test, KHÔNG substitute.
- "Stdio proxy skip relay form vì pre-configured / chỉ cần handshake" (2026-04-21) → SAI. Stdio proxy = server expose stdio nhưng bên trong spawn LOCAL `runLocalServer`/`run_local_server` relay form khi config.enc trống. Phase 2 clean-state bắt buộc config trống → stdio PHẢI exercise form flow giống http local-relay. Exception duy nhất: server KHÔNG có relay (better-godot-mcp).
- "Test A (MCP protocol) + Test B (Claude Code + Copilot plugin install) gộp chung" (2026-04-21) → violates `feedback_work_order_fix_test_release.md`. Test A uses source code + Python MCP SDK pre-release. Test B uses published artifact + real client post-release. Release sits BETWEEN. "Configure plugin on Claude Code/Copilot" là Phase 6 work, không phải Phase 3.

## References (load as needed)

- `references/scope-and-repos.md` — 12 repos canonical list + vocab
- `references/mode-matrix.md` — 7 servers × modes + mode definitions + anti-patterns
- `references/tool-layout.md` — N+2 standard (domain + config + help) + Python/TS templates
- `references/config-parity.md` — category parity rules
- `references/relay-flow.md` — local ≡ remote UI parity + credential state machine
- `references/reuse-mcp-core.md` — primitives to reuse (storage/relay/OAuth AS/browser/lock/state)
- `references/audit-commands.md` — gh CLI commands with `--limit 1000`
- `references/backlog-allowlist.md` — auto-allowed + explicit long-running
- `references/backlog-clearance.md` — priority order + per-PR review protocol
- `references/clean-state.md` — per-server clean paths (config.enc, token cache, session lock)
- `references/e2e-full-matrix.md` — 17 configs table + uniform 9-step procedure (Test A)
- `references/release-cascade.md` — PSR dispatch order + downstream auto-issue verify
- `references/client-integration-test.md` — Phase 6 Test B: Claude Code + Copilot plugin install verify
- `references/real-plugin-verification.md` — 4 yêu cầu verify thực tế trên Claude Code (secret saved + tool/action call THROUGH Claude Code + 1 daemon per server + single/multi user)
- `references/non-mcp-repos.md` — qwen3-embed / web-core / claude-plugins / n24q02m checks
- `references/readme-parity.md` — README tier + parity across Productions/Scripts Stars lists (27 repos)
- `references/multi-user-pattern.md` — PUBLIC_URL + per-JWT-sub credential storage recipe (added 2026-04-26 with 4-server migration cascade)

## Memory (incident log — why history)

Canonical "how to apply" = reference files above. For incident history (violations + why rules exist), see memory:

- `feedback_work_order_fix_test_release.md` — FIX → TEST → RELEASE order + EMPTY BACKLOG gate
- `feedback_mcp_mode_matrix.md` — mode matrix history (E2E flipped default→full 2026-04-20)
- `feedback_mcp_config_parity.md` — category parity violations
- `feedback_relay_mode_ui_parity.md` — local ≡ remote UI parity violations
- `feedback_e2e_clean_state_all_servers.md` — clean state before E2E
- `feedback_full_live_test.md` — relay flow thật, no env inject
- `feedback_pr_review_must_be_real.md` — full diff review (Jules PR case)
- `feedback_data_store_no_guessing.md` — data store attributes per server
- `feedback_core_release_auto_issue.md` — downstream tracking issue on core release
- `feedback_psr_auto_version.md` — never manual version pick
- `feedback_test_before_release.md` — merge → E2E on main → release last (private repos)
- `scope-12-repos.md` — 12 repo canonical list
- `mcp-server-data-stores.md` — per-server data store truth table
- `feedback_mcp_dev_skill.md` — this skill trigger memory (invocation criteria)

## Skill versioning

Skill version is implicit in profile repo commit SHA. To find canonical: `git log -1 --format=%H -- ~/.claude/skills/mcp-dev/SKILL.md` in `n24q02m/n24q02m` public repo clone.
