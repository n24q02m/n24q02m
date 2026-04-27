# E2E Full Matrix — Phase 3 (Test A: MCP Protocol, Pre-Release)

Phase 3 của mcp-dev cascade. **Test A — MCP PROTOCOL E2E trên SOURCE CODE**, chạy TRƯỚC release. Entered sau khi Phase 2 (clean-state reset — xem `clean-state.md`) complete. Exit khi **19/19 configs PASS** (post-imagine-mcp 2026-04-24).

**2026-04-26 update — T0/T2 driver overlay**: Configs này được automation hoá qua `mcp-core/scripts/e2e/` driver theo mode-matrix.md section 7 (16-config 3-axis taxonomy). T0 (5 configs no-upstream) chạy auto trong CI/precommit. T2 (11 configs có cred) chạy local manual `make e2e-full` — driver auto fill relay form, in user-gate URL ra stderr cho upstream OAuth/OTP/device-code (KHÔNG automation per `feedback_relay_fill_all_fields.md`). Manual procedure section 3 dưới đây vẫn là source of truth khi driver fail hoặc cần debug từng step. Spec + plan canonical: `.superpower/mcp-core/{specs,plans}/2026-04-25-e2e-framework-and-multi-user-migration.md`. Multi-user remote (PUBLIC_URL) deployment property mới — xem `multi-user-pattern.md`.

**2026-04-27 update — HARNESS-FIRST gate trước khi run matrix**: Trước khi `make e2e-full` hoặc start bất kỳ T2 config nào, BẮT BUỘC qua "Harness Readiness checklist" (xem memory `feedback_harness_first_no_run_fix_cycle.md`):

1. Read latest `<memory>/e2e-execution-audit-*.md` failure-mode catalog (16+ modes accumulated 2 tuần qua).
2. Verify driver source cover hết: per-flow timeout (device-code 900s / oauth-redirect 300s / browser-form 600s), health probe pre-prompt, live elapsed/remaining display 30s/lần, echo poll body, graceful timeout teardown (capture container logs + setup-status TRƯỚC `docker compose down`), one-time setup checklist banner ở batch start, driver dispatch theo `flow:` field, creds shape adapter per-server.
3. Cấm pattern "start config N → bug → fix → restart → config N+1 → bug khác → fix → restart". Gặp failure mode mới giữa session: STOP, append catalog, fix harness, restart từ config 1.
4. Cấm config require user out-of-band setup mỗi run (register `http://127.0.0.1:<port>/callback` ở Notion app, pin port vào dashboard, grant account, ...) — xem memory `feedback_no_out_of_band_test_setup.md`. 3 lựa chọn valid: (a) prod-stable callback + tunnel, (b) driver-controlled tunnel + provider DCR API, (c) loopback OAuth provider chấp nhận `http://127.0.0.1:<any>` (Google Desktop). Không thoả mãn → reclassify khỏi T2 matrix.

Status report cấm "X/N PASS, stuck ở config K" khi chưa qua Harness Readiness. Phải là "Harness Readiness M/M PASS → bắt đầu E2E sequential" hoặc "Harness Readiness K/M, blocker: ..., chưa start matrix".

**Test A scope**: Server từ source code (`uv run <server>` / `bun run build && node bin/cli.mjs`). Client = em via Python MCP SDK (`mcp.ClientSession` + `stdio_client` / `streamablehttp_client`). Verify protocol works end-to-end BEFORE publishing broken binary.

**NOT this phase**: Plugin install trên Claude Code CLI / VS Code Copilot. Đó là **Test B (Phase 6)** — xem `client-integration-test.md`. 2026-04-21 violation: em gộp Test A + Test B, user corrected: "Test qua mcprotocol đã, rồi mới release stable, thì mới có cái mà test với plugin".

## 1. Policy Change History

**2026-04-20**: Trước đó chỉ cover default mode mỗi server → 7 configs. Đủ MVP nhưng miss bug ở non-default modes. Expanded to FULL MATRIX — 24 configs = 20 MCP (3 modes × credentialed + 2 × godot) + 4 non-MCP.

**2026-04-23 (1-Daemon merge)**: stdio proxy + http local-relay **collapsed to single `daemon` mode** vì chúng chạy cùng backend (`runSmartStdioProxy` TS / `run_smart_stdio_proxy` Python). Matrix từ 24 → **17 configs = 13 MCP + 4 non-MCP**. Justification:
- Post-merge, "stdio proxy" là wrapper mỏng gọi `runSmartStdioProxy` → spawn cùng LOCAL HTTP daemon giống local-relay. Cred form, relay_schema, storage paths, `authorize` endpoint — identical.
- Khác duy nhất là CLIENT-side transport (stdio pipe vs HTTP). Test A verify MCP PROTOCOL trên cùng daemon backend — both transports exercised via 1 cred setup + 2 client connections (stdio_client + streamablehttp_client) trong daemon mode.
- Configs giảm nhưng coverage KHÔNG giảm: mỗi daemon config test cả 2 transports.

**2026-04-24 (+imagine-mcp)**: Thêm MCP server thứ 8 (`imagine-mcp`, image/video understand+generate, default `daemon`, alt `remote-relay (self-host)`). Matrix 17 → **19 configs = 15 MCP + 4 non-MCP**. imagine-mcp cùng category wet/mnemo/crg (default local-relay, 3 API key fields Gemini/OpenAI/Grok, all optional) → 2 configs mới (daemon default + remote-relay self-host) xen giữa godot (prev #13) và non-MCP (prev #14-17); godot dời xuống #15 để giữ block MCP configs contiguous.

## 2. Full 19-Config Table

**CI-verified tag**: 5 configs auto-run on every push/PR (no manual test needed — CI green = PASS):
- `#15` better-godot-mcp local → `bun run test:live` (stdio handshake + tools/list covers both transports environment-agnostic)
- `#16` qwen3-embed → `uv run pytest -m "not integration"` includes shape assertions
- `#17` web-core → `uv run pytest` covers `test_search/test_runner.py` + `test_runner_security.py`
- `#18` claude-plugins → `python3 scripts/validate_marketplace.py` (CI `validate` job + precommit hook)
- `#19` n24q02m → `markdownlint-cli` + lychee link check (CI `validate` job + precommit hook)

**Manual user interaction** (remaining 14 configs `#1-14`): OAuth / OTP / real provider flows cannot be automated — user must drive browser per `feedback_relay_fill_all_fields.md`.

| # | Repo | Mode | Activation | Credential flow | Expected state event |
|---|------|------|------------|-----------------|----------------------|
| 1 | better-notion-mcp | remote-oauth (default) | Connect plugin to `https://better-notion-mcp.n24q02m.com` | Notion OAuth provider redirect → callback | JWT issued, `config(status).state=configured` + `has_token=true` after provider callback |
| 2 | better-notion-mcp | daemon | `npx @n24q02m/better-notion-mcp` (stdio) or `MCP_MODE=local-relay` (http) — same `runSmartStdioProxy` spawns local `/authorize` form | Paste Notion integration token (`ntn_...`) at `http://127.0.0.1:<port>/authorize` | `state=configured` after form submit; test BOTH stdio_client + streamablehttp_client against same daemon |
| 3 | better-email-mcp | remote-relay (default) | Connect plugin to `https://better-email-mcp.n24q02m.com` | Multi-provider form (Gmail/Yahoo/iCloud/Outlook) | `state=configured` after form submit, per-JWT-sub accounts list populated |
| 4 | better-email-mcp | daemon | `npx @n24q02m/better-email-mcp` (stdio) or `MCP_MODE=local-relay` (http) — same daemon | Same multi-provider form at local `/authorize` | `state=configured` after form submit; test both transports |
| 5 | better-telegram-mcp | remote-relay (default) | Connect plugin to `https://better-telegram-mcp.n24q02m.com` | Phone + OTP multi-step | `state=configured` after OTP verify |
| 6 | better-telegram-mcp | daemon | `uvx better-telegram-mcp` (stdio) or `MCP_MODE=local-relay` (http) — same daemon | Phone + OTP via local form | `state=configured` after OTP verify; test both transports |
| 7 | wet-mcp | daemon (default) | `uvx wet-mcp` (stdio) or http — same daemon | 4 password fields (Jina/Gemini/OpenAI/Cohere), all `required: false`; fill ALL với cred thật per `feedback_relay_fill_all_fields.md` | `state=configured` after form submit; test both transports |
| 8 | wet-mcp | remote-relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<user-deployed-url> uvx wet-mcp` | Same 4-field form, remote URL; fill ALL | `state=configured` after form submit |
| 9 | mnemo-mcp | daemon (default) | `uvx mnemo-mcp` (stdio) or http — same daemon | 4 password fields; fill ALL | `state=configured` after form submit; test both transports |
| 10 | mnemo-mcp | remote-relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx mnemo-mcp` | Same 4-field form, remote | `state=configured` after form submit |
| 11 | better-code-review-graph | daemon (default) | `uvx better-code-review-graph` (stdio) or http — same daemon | 4 password fields; fill ALL | `state=configured` after form submit; test both transports |
| 12 | better-code-review-graph | remote-relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx better-code-review-graph` | Same 4-field form, remote | `state=configured` after form submit |
| 13 | imagine-mcp | daemon (default) | `uvx imagine-mcp` (stdio) or http — same daemon | 3 password fields (GEMINI / OPENAI / XAI; renamed 2026-04-26 `GOOGLE_AI_STUDIO_API_KEY` → `GEMINI_API_KEY`), all `required: false`; fill ALL với cred thật per `feedback_relay_fill_all_fields.md` | `state=configured` after form submit; test both transports |
| 14 | imagine-mcp | remote-relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx imagine-mcp` | Same 3-field form, remote | `state=configured` after form submit |
| 15 | better-godot-mcp | local (default) | `npx @n24q02m/better-godot-mcp` (stdio) or http | No credentials | `state=configured` on launch (immediate); verify both transports |
| 16 | qwen3-embed | pytest + smoke | `cd ~/projects/qwen3-embed && uv run pytest -m "not integration"` + embed smoke | N/A (library) | `pytest exit 0` + smoke returns shape `(1, N)` |
| 17 | web-core | pytest + SearXNG runner | `cd ~/projects/web-core && uv run pytest` + `uv run python -m web_core.searxng.runner --check` | N/A | `pytest exit 0` + "SearXNG ready at http://127.0.0.1:8888" |
| 18 | claude-plugins | validate marketplace | `python3 scripts/validate_marketplace.py` + `jq . .claude-plugin/marketplace.json` | N/A | validator "All N plugins validated" + jq exit 0 |
| 19 | n24q02m profile | markdownlint + linkcheck + secret-scan | `npx markdownlint-cli '**/*.md'` + `grep -rE '<secret-patterns>' . --include='*.md'` | N/A | markdown lint 0 + no non-doc secret matches |

## 2.5 Semantics: "daemon" mode

**Daemon mode** trong matrix = **1-Daemon merged flow** (local-relay + stdio-proxy gộp thành một). Applies tới 7 credentialed servers (notion/email/telegram/wet/mnemo/crg/imagine). Flow:

1. User chạy server (stdio invocation: `uvx <server>` / `npx @n24q02m/<server>`, hoặc HTTP: `MCP_MODE=local-relay`)
2. Backend `runSmartStdioProxy` (TS) hoặc `run_smart_stdio_proxy` (Python) detect empty `config.enc`
3. Backend spawn LOCAL `runLocalServer` / `run_local_server` trên random 127.0.0.1 port với `relaySchema` của server đó
4. Backend print relay URL tới stderr + (best-effort) mở browser
5. User paste creds vào form tại `http://127.0.0.1:<port>/authorize`, submit
6. `onCredentialsSaved` callback ghi `config.enc`, set `_state=configured`
7. Client transport:
   - **stdio client** (stdio_client): dùng cùng process stdio pipe; tool calls flow stdin/stdout JSON-RPC
   - **http client** (streamablehttp_client): connect `http://127.0.0.1:<port>/mcp` trên CÙNG daemon (client-side switch, daemon KHÔNG quan tâm)

**Test A verification cho daemon config**:
- Clean state → launch stdio subprocess → user fill form (1 lần) → state=configured
- Run `stdio_client` → initialize + tools/list + tools/call(config, help) + functional domain call → pass ✓
- Daemon process lifecycle bound to spawning stdio subprocess — khi stdio exit, daemon cũng exit. KHÔNG feasible connect streamablehttp_client cùng lúc vì lock token in-process không expose.
- HTTP transport của cùng server được verify qua remote-* config (cùng `streamablehttp_client` code path): notion `#1 remote-oauth`, email `#3 remote-relay`, telegram `#5 remote-relay`, wet/mnemo/crg `#8/#10/#12 remote-relay self-host`.
- godot `#15` không cred → chỉ chạy `bun run test:live` cover cả stdio + http qua live test.

## 2.6 Pre-Matrix Smoke: catch shared transport bugs EARLY

BẮT BUỘC trước khi chạy config #1: verify `run_smart_stdio_proxy` (Python) + `runSmartStdioProxy` (TS) mỗi cái OK với 1 server tượng trưng. Mục đích: bắt regression dùng chung (vd `httpx_sse` Accept override → FastMCP 406, xem `feedback_httpx_sse_accept_override.md`) trước khi tốn thời gian chạy toàn bộ matrix.

- **Python smoke (1 phút)**: `uvx <any-python-mcp>` + `mcp stdio_client` → `tools/list`. Nếu lỗi `Initial POST /mcp returned 406` → fix mcp-core smart_stdio, KHÔNG tiếp tục matrix. Python servers: wet, mnemo, crg, telegram, imagine.
- **TS smoke (1 phút)**: `node bin/cli.mjs` (stdio) + `mcp stdio_client` → `tools/list`. TS servers: notion, email, godot.

Nếu smoke fail: fix root cause + re-run smoke. Chỉ khi CẢ 2 smoke PASS mới bắt đầu matrix config #1.

## 3. Per-Config Procedure (uniform 10 steps for configs #1-15)

```
[pre]  Clean state (see clean-state.md): run clean_state for this server

[1]    Launch: $ACTIVATION_CMD from table → wait ~2-5s for server ready
       Verify: stderr shows "Server listening on ..." or equivalent

[2]    Relay URL or OAuth redirect appears (skip for godot + pre-configured modes)
       Verify: URL printed to stderr or accessible at 127.0.0.1:<port>

[3]    User action in browser (REAL user, KHÔNG automation, KHÔNG programmatic POST):
         - remote-oauth: click Connect → provider login → callback
         - remote-relay / daemon: paste credentials at /authorize form —
           FILL MỌI FIELD kể cả `required: false` bằng credential thật;
           submit-empty/skip-optional = KHÔNG pass, vi phạm section 6

[4]    Server emits state=configured event (monitor stderr log)
       Verify: log line contains "state=configured" or equivalent

[5]    MCP client (transport variant A): connect + initialize + tools/list
       - remote-oauth / remote-relay: streamablehttp_client with OAuth
       - daemon: stdio_client first (primary transport)
       Verify: N+2 layout present (domain tools + `config` + `help`)

[6]    For at least one domain tool: tools/call with representative args
       Verify: output shape matches tool schema, functional data returned
       (remote-oauth: workspace(info) etc.; daemon: same)

[7]    tools/call config(action="status")
       Verify: state=configured in response, has_token=true (or equivalent
       per-user readiness marker)

[8]    tools/call help()
       Verify: valid topics list returned (contains all domain tool names + "config")

[9]    Teardown: kill server process. Preserve config.enc UNTIL cross-mode
       verification done; clean before moving to next different-mode config.
```

Configs #16-19 (non-MCP): custom steps per repo — xem `non-mcp-repos.md` chi tiết.

## 4. ALL GREEN Gate

**19/19 PASS bắt buộc** trước khi exit Phase 3. Bất kỳ config nào fail → **back to Phase 1 (`backlog-clearance.md`)**, không được skip forward hay "fix sau". Root cause fix + re-run scenario (tuân `feedback_fix_root_cause_verify.md`).

## 5. Checkpoint Marker (Resumable Cascade)

- Record last passed config `N` trong `cascade-<date>-phase3-results.md`.
- Resume from config `N+1` next session — không re-run configs đã PASS.
- Evidence required per config:
  - `config.enc` bytes before/after (proof state persisted)
  - Relay URL hoặc OAuth redirect URL
  - `state=configured` timestamp
  - Tool call outputs (step 6-8) — full JSON, không trim
  - Server stderr log (relevant lines)
  - Daemon mode: separate evidence blocks for stdio transport vs http transport

## 6. Anti-patterns (CẤM)

- Skip optional fields trong cred form ("required: false" = fill hoặc skip tùy em" — SAI, phải fill per `feedback_relay_fill_all_fields.md`)
- Browser automation (Playwright/Puppeteer/Selenium) thay user click — per `feedback_relay_fill_all_fields.md`
- Curl `/health` thay MCP protocol handshake — không verify MCP semantics
- Claim PASS khi chỉ test 1 transport của daemon mode — phải test cả stdio + http
- Skip daemon mode vì "local-relay đã test rồi" — không còn local-relay riêng sau 2026-04-23
- Skip stdio mode vì "daemon đã test" — stdio là 1 trong 2 transports của daemon, phải verify
- Reuse config.enc giữa configs cross-mode (vd daemon config.enc bleed into remote-relay test) — clean-state per config
