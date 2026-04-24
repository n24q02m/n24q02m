# E2E Full Matrix — Phase 3 (Test A: MCP Protocol, Pre-Release)

Phase 3 của mcp-dev cascade. **Test A — MCP PROTOCOL E2E trên SOURCE CODE**, chạy TRƯỚC release. Entered sau khi Phase 2 (clean-state reset — xem `clean-state.md`) complete. Exit khi **24/24 configs PASS**.

**Test A scope**: Server từ source code (`uv run <server>` / `bun run build && node bin/cli.mjs`). Client = em via Python MCP SDK (`mcp.ClientSession` + `stdio_client` / `streamablehttp_client`). Verify protocol works end-to-end BEFORE publishing broken binary.

**NOT this phase**: Plugin install trên Claude Code CLI / VS Code Copilot. Đó là **Test B (Phase 6)** — xem `client-integration-test.md`. 2026-04-21 violation: em gộp Test A + Test B, user corrected: "Test qua mcprotocol đã, rồi mới release stable, thì mới có cái mà test với plugin".

## 1. Policy Change (2026-04-20)

Trước 2026-04-20: E2E chỉ cover default mode mỗi server ("default TRƯỚC, modes khác sau nếu spec yêu cầu") -> 7 configs. Đủ MVP nhưng miss bug ở non-default modes.

Từ 2026-04-20: **FULL MATRIX** — test **ALL modes** per server. Tổng cộng 17 configs = 13 MCP (mỗi server x mỗi mode sau khi gộp 1-Daemon) + 4 non-MCP (qwen3-embed, web-core, claude-plugins, n24q02m profile).

**Justification**:
- 13 / 20 MCP configs trước đây chưa bao giờ test end-to-end (chỉ unit + smoke).
- Incident 2026-04-19 (email-mcp): remote-relay code path ép Outlook only, local-relay có paste form multi-provider -> drift silently vì remote-relay không trong E2E matrix.
- Release cascade (mcp-core bump -> 7 MCP bumps) dễ breakage ở non-default modes vì CI green chỉ verify default. User chạy `MCP_MODE=local-relay` trên server có OAuth config -> gặp bug không ai test.

## 2. Full 17-Config Table

**CI-verified tag**: 5 configs auto-run on every push/PR (no manual test needed — CI green = PASS):
- `#13` better-godot-mcp 1-Daemon (http local / stdio proxy) → `bun run test:live` (stdio handshake + tools/list, environment-agnostic)
- `#14` qwen3-embed → `uv run pytest -m "not integration"` includes shape assertions (`test_custom_text_embedding.py` shape `(1,8)` / `(2,4)`)
- `#15` web-core → `uv run pytest` covers `test_search/test_runner.py` + `test_runner_security.py`
- `#16` claude-plugins → `python3 scripts/validate_marketplace.py` (CI `validate` job + precommit hook)
- `#17` n24q02m → `markdownlint-cli` + lychee link check (CI `validate` job + precommit hook)

**Manual user interaction** (remaining 12 configs `#1-12`): OAuth / OTP / real provider flows cannot be automated — user must drive browser per `feedback_relay_fill_all_fields.md`.

| # | Repo | Mode | Activation | Credential flow | Expected state event |
|---|------|------|------------|-----------------|----------------------|
| 1 | better-notion-mcp | http remote oauth (default) | Connect plugin to `https://notion-mcp.n24q02m.com` | Notion OAuth provider redirect -> callback | `state=configured` after callback |
| 2 | better-notion-mcp | 1-Daemon (http local / stdio proxy) | `MCP_TRANSPORT=stdio npx @n24q02m/better-notion-mcp` | Clean config.enc → server spawns LOCAL `runLocalServer` relay form at `http://127.0.0.1:<port>/authorize`; user fills Notion token + submits | `state=configured` after form submit, stdio session resumes with saved cred |
| 3 | better-email-mcp | http remote relay (default) | Connect plugin to `https://email-mcp.n24q02m.com` | Multi-provider form (Gmail/Yahoo/iCloud/Outlook) | `state=configured` after form submit |
| 4 | better-email-mcp | 1-Daemon (http local / stdio proxy) | `MCP_TRANSPORT=stdio npx @n24q02m/better-email-mcp` | Clean config.enc → server spawns LOCAL `runLocalServer` relay form; user fills multi-provider creds + submits | `state=configured` after form submit, stdio session resumes |
| 5 | better-telegram-mcp | http remote relay (default) | Connect plugin to `https://telegram-mcp.n24q02m.com` | Phone number + OTP code | `state=configured` after OTP verify |
| 6 | better-telegram-mcp | 1-Daemon (http local / stdio proxy) | `MCP_TRANSPORT=stdio uvx better-telegram-mcp` | Clean config.enc → server spawns LOCAL `run_local_server` relay form; user fills bot_token + phone/OTP + submits | `state=configured` after OTP verify, stdio session resumes |
| 7 | wet-mcp | 1-Daemon (http local / stdio proxy) (default) | `MCP_TRANSPORT=stdio uvx wet-mcp` | Clean config.enc → server spawns LOCAL `run_local_server` relay form (4 password fields); fill ALL + submit | `state=configured` after form submit, stdio session resumes |
| 8 | wet-mcp | http remote relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx wet-mcp` | Same 4-field form, remote URL; fill ALL | `state=configured` after form submit |
| 9 | mnemo-mcp | 1-Daemon (http local / stdio proxy) (default) | `MCP_TRANSPORT=stdio uvx mnemo-mcp` | Clean config.enc → server spawns LOCAL `run_local_server` relay form (4 password fields); fill ALL + submit | `state=configured` after form submit, stdio session resumes |
| 10 | mnemo-mcp | http remote relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx mnemo-mcp` | Same 4-field form, remote URL; fill ALL | `state=configured` after form submit |
| 11 | better-code-review-graph | 1-Daemon (http local / stdio proxy) (default) | `MCP_TRANSPORT=stdio uvx better-code-review-graph` | Clean config.enc → server spawns LOCAL `run_local_server` relay form (4 password fields); fill ALL + submit | `state=configured` after form submit, stdio session resumes |
| 12 | better-code-review-graph | http remote relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx better-code-review-graph` | Same 4-field form, remote URL; fill ALL | `state=configured` after form submit |
| 13 | better-godot-mcp | 1-Daemon (http local non-relay / stdio proxy) | `MCP_TRANSPORT=stdio npx @n24q02m/better-godot-mcp` | No credentials (godot không dùng relay); verify MCP handshake + tools/list | `state=configured` on launch (immediate) |
| 14 | qwen3-embed | pytest + smoke | `cd ~/projects/qwen3-embed && uv run pytest tests/` + embed smoke | N/A (library) | `pytest exit 0` + smoke returns shape `(1, N)` |
| 15 | web-core | pytest + SearXNG runner | `cd ~/projects/web-core && uv run pytest tests/` + `uv run python -m web_core.searxng.runner --check` | N/A | `pytest exit 0` + "SearXNG ready at http://127.0.0.1:8888" |
| 16 | claude-plugins | jq + lint + dry-run install | `jq . plugins/*/plugin.json` + `node scripts/lint-marketplace.js` + `claude plugin install <name> --dry-run` per MCP | N/A | jq exit 0 + lint exit 0 + dry-run no FAIL |
| 17 | n24q02m profile | markdownlint + linkcheck + secret-scan | `npx markdownlint-cli '**/*.md'` + link-check CLAUDE.md/MEMORY.md + grep for inline secrets | N/A | markdown lint 0 + no broken links + no secret matches |

## 3. Per-Config Procedure (uniform 9 steps for configs #1-12)

```
[pre]  Clean state (see clean-state.md): run `clean_state <server>`

[1]    Launch: $ACTIVATION_CMD from table -> wait ~2-5s for server ready
       Verify: stderr shows "Server listening on ..." or equivalent

[2]    Relay URL or OAuth redirect appears (skip for godot + stdio modes if cred already present)
       Verify: URL printed to stderr or accessible at 127.0.0.1:<port>

[3]    User action in browser (REAL user, KHÔNG automation, KHÔNG programmatic POST):
         - remote-oauth: click Connect -> provider login -> callback
         - remote-relay / local-relay: paste credentials at /authorize form —
           FILL MỌI FIELD kể cả `required: false` bằng credential thật;
           submit-empty/skip-optional = KHÔNG pass, vi phạm section 6
         - stdio-proxy: với CLEAN state (config.enc trống, bắt buộc per
           `clean-state.md`), server spawns LOCAL `runLocalServer` / `run_local_server`
           relay form tại `http://127.0.0.1:<port>/authorize` (xem `feedback_stdio_fallback_local_only.md`).
           USER PHẢI mở browser + fill MỌI field giống mode http-local-relay +
           submit. KHÔNG skip như http mode. Exception duy nhất: server không
           dùng relay (godot #13) hoặc config đã có ở session khác của
           CÙNG matrix run (không clean giữa mode của cùng server = vi phạm
           clean-state rule).

[4]    Server emits state=configured event (monitor stderr log)
       Verify: log line contains "state=configured" or equivalent

[5]    MCP client: connect + initialize + tools/list
       Verify: N+2 layout present (domain tools + `config` + `help`)

[6]    For each domain tool: tools/call with representative args
       Verify: output shape matches tool schema

[7]    tools/call config(action="status")
       Verify: state=configured in response

[8]    tools/call help()
       Verify: valid topics list returned (contains all domain tool names + "config")

[9]    Teardown: kill server process, preserve config.enc for stdio-proxy mode test next
```

Configs #14-17 (non-MCP): custom steps per repo — xem `non-mcp-repos.md` chi tiết.

## 4. ALL GREEN Gate

**17/17 PASS bắt buộc** trước khi exit Phase 3. Bất kỳ config nào fail -> **back to Phase 1 (`backlog-clearance.md`)**, không được skip forward hay "fix sau". Root cause fix + re-run scenario (tuân `feedback_fix_root_cause_verify.md`).

## 5. Checkpoint Marker (Resumable Cascade)

- Record last passed config `N` trong `cascade-<date>-phase3-results.md`.
- Resume from config `N+1` next session — không re-run configs đã PASS.
- Evidence required per config:
  - `config.enc` bytes before/after (proof state persisted)
  - Relay URL hoặc OAuth redirect URL
  - `state=configured` timestamp
  - Tool call outputs (step 6-8) — full JSON, không trim
  - Server stderr log (relevant lines)

## 6. Anti-patterns (CẤM)

- **"Test only default mode"** -> violate full-matrix rule (policy flip 2026-04-20).
- **"Inject env var to skip relay"** -> violate `feedback_full_live_test.md`. Infisical creds là server config, KHÔNG phải test shortcut.
- **"Already configured, skip step [1]"** -> violate clean-state rule. Mỗi config PHẢI clean-state trước launch.
- **"Test all configs in parallel"** -> E2E requires user interaction per config (OTP, OAuth click); parallel tạo race conditions + user không phản hồi kịp.
- **"Mock the relay server"** -> defeat end-to-end purpose. Relay code path chính là cái cần test.
- **"CI green nên skip E2E"** -> CI chỉ verify build+unit+integration mock. E2E verify user-facing flow thật.
- **"Default mode PASS rồi, non-default chắc OK"** -> drift incident 2026-04-19 chứng minh ngược lại.
- **"Optional field rỗng cũng OK, skip đi"** (2026-04-21) -> CẤM TUYỆT ĐỐI. Khi test relay, MỌI field (cả `required: true` lẫn `required: false`) PHẢI được fill bằng credential thật. Lý do: (1) optional field thường cover critical code path — `onCredentialsSaved` callback có branches theo từng field có value hay không; (2) submit-empty chỉ verify fallback branch, bỏ qua validation/normalization/persistence logic cho từng field; (3) cross-provider priority logic (vd `JINA > GEMINI > OPENAI > COHERE`) chỉ lộ bug khi có nhiều key cùng lúc; (4) "empty submit OK = pass" = giả mạo E2E coverage. Nếu thiếu credential cho optional field → pause test + xin user cung cấp, KHÔNG skip.
- **"Browser automation (Playwright/Puppeteer/Selenium) để thay click user"** (2026-04-21) -> CẤM. User-action trong skill step [3] là bắt buộc user THẬT, không phải script. Browser automation = mock layer: không exercise OAuth redirect với real provider consent, không render real form + CSS + CSP, không submit via real click event listener, không replay real browser JWT cookie flow. Programmatic POST tới submit endpoint cũng cấm vì cùng lý do. Nếu user không có sẵn để participate → pause test, KHÔNG substitute automation.

## 7. Rule Summary

- **13 MCP configs** × 9 steps uniform + **4 non-MCP configs** × custom steps = **17 total**.
- All MCP configs require user interaction for credential step (except stdio modes reuse prior cred from config.enc — vẫn phải có step [4] state verify).
- Clean state per server **before each config** — bao gồm mode khác nhau của cùng 1 server.
- **NEVER skip to Phase 4 with <17 green.**
- Relay flow -> config saved -> restart server -> MCP protocol test. One continuous chain per `feedback_relay_then_protocol.md`.

## 8. Cross-References

- `mode-matrix.md` — mode definitions + supported modes per server (source of truth matrix).
- `clean-state.md` — pre-launch state reset procedure (xóa `config.enc`, token cache, session lock).
- `non-mcp-repos.md` — detail procedure cho configs #21-24.
- `feedback_full_live_test.md` — no env var shortcut rule, creds là server config không phải test bypass.
- `feedback_relay_then_protocol.md` — relay setup BEFORE protocol test, one continuous chain.
- `feedback_e2e_clean_state_all_servers.md` — clean-state mỗi server, không skip phase 1 dù đã configured.
- `feedback_fix_root_cause_verify.md` — fail config -> fix root cause + re-run scenario.
- `audit-commands.md` — gh commands cho empty-backlog gate (Phase 1).
- `backlog-clearance.md` — Phase 1 procedure, quay về đây nếu config fail.
