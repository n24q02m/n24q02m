# E2E Full Matrix — Phase 3 Cascade

Phase 3 của mcp-dev cascade. Entered **sau khi** Phase 2 (clean-state reset — xem `clean-state.md`) complete trên mọi server trong scope. Exit khi **24/24 configs PASS**.

## 1. Policy Change (2026-04-20)

Trước 2026-04-20: E2E chỉ cover default mode mỗi server ("default TRƯỚC, modes khác sau nếu spec yêu cầu") -> 7 configs. Đủ MVP nhưng miss bug ở non-default modes.

Từ 2026-04-20: **FULL MATRIX** — test **ALL modes** per server. Tổng cộng 24 configs = 20 MCP (mỗi server x mỗi mode) + 4 non-MCP (qwen3-embed, web-core, claude-plugins, n24q02m profile).

**Justification**:
- 13 / 20 MCP configs trước đây chưa bao giờ test end-to-end (chỉ unit + smoke).
- Incident 2026-04-19 (email-mcp): remote-relay code path ép Outlook only, local-relay có paste form multi-provider -> drift silently vì remote-relay không trong E2E matrix.
- Release cascade (mcp-core bump -> 7 MCP bumps) dễ breakage ở non-default modes vì CI green chỉ verify default. User chạy `MCP_MODE=local-relay` trên server có OAuth config -> gặp bug không ai test.

## 2. Full 24-Config Table

| # | Repo | Mode | Activation | Credential flow | Expected state event |
|---|------|------|------------|-----------------|----------------------|
| 1 | better-notion-mcp | http remote oauth (default) | Connect plugin to `https://notion-mcp.n24q02m.com` | Notion OAuth provider redirect -> callback | `state=configured` after callback |
| 2 | better-notion-mcp | http local relay | `MCP_MODE=local-relay npx @n24q02m/better-notion-mcp` | Paste Notion integration token at `http://127.0.0.1:<port>/authorize` | `state=configured` after form submit |
| 3 | better-notion-mcp | stdio proxy | `MCP_TRANSPORT=stdio npx @n24q02m/better-notion-mcp` | Pre-configured (from mode 1 or 2) | `state=configured` on launch |
| 4 | better-email-mcp | http remote relay (default) | Connect plugin to `https://email-mcp.n24q02m.com` | Multi-provider form (Gmail/Yahoo/iCloud/Outlook) | `state=configured` after form submit |
| 5 | better-email-mcp | http local relay | `MCP_MODE=local-relay npx @n24q02m/better-email-mcp` | Same multi-provider form at `http://127.0.0.1:<port>/authorize` | `state=configured` after form submit |
| 6 | better-email-mcp | stdio proxy | `MCP_TRANSPORT=stdio npx @n24q02m/better-email-mcp` | Pre-configured (from mode 4 or 5) | `state=configured` on launch |
| 7 | better-telegram-mcp | http remote relay (default) | Connect plugin to `https://telegram-mcp.n24q02m.com` | Phone number + OTP code | `state=configured` after OTP verify |
| 8 | better-telegram-mcp | http local relay | `MCP_MODE=local-relay uvx better-telegram-mcp` | Phone + OTP via local form | `state=configured` after OTP verify |
| 9 | better-telegram-mcp | stdio proxy | `MCP_TRANSPORT=stdio uvx better-telegram-mcp` | Pre-configured | `state=configured` on launch |
| 10 | wet-mcp | http local relay (default) | `uvx wet-mcp` | 4 optional API keys (Jina/Gemini/OpenAI/Cohere), all empty -> skip | `state=configured` after form submit |
| 11 | wet-mcp | http remote relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx wet-mcp` | Same form, remote URL | `state=configured` after form submit |
| 12 | wet-mcp | stdio proxy | `MCP_TRANSPORT=stdio uvx wet-mcp` | Pre-configured | `state=configured` on launch |
| 13 | mnemo-mcp | http local relay (default) | `uvx mnemo-mcp` | Empty form (SQLite local, no creds needed) | `state=configured` after Skip |
| 14 | mnemo-mcp | http remote relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx mnemo-mcp` | Empty form remote | `state=configured` after Skip |
| 15 | mnemo-mcp | stdio proxy | `MCP_TRANSPORT=stdio uvx mnemo-mcp` | Pre-configured | `state=configured` on launch |
| 16 | better-code-review-graph | http local relay (default) | `uvx better-code-review-graph` | Empty form (SQLite local) | `state=configured` after Skip |
| 17 | better-code-review-graph | http remote relay (self-host) | `MCP_MODE=remote-relay MCP_RELAY_URL=<url> uvx better-code-review-graph` | Empty form remote | `state=configured` after Skip |
| 18 | better-code-review-graph | stdio proxy | `MCP_TRANSPORT=stdio uvx better-code-review-graph` | Pre-configured | `state=configured` on launch |
| 19 | better-godot-mcp | http local non-relay (default) | `npx @n24q02m/better-godot-mcp` | No credentials | `state=configured` on launch (immediate) |
| 20 | better-godot-mcp | stdio proxy | `MCP_TRANSPORT=stdio npx @n24q02m/better-godot-mcp` | No credentials | `state=configured` on launch (immediate) |
| 21 | qwen3-embed | pytest + smoke | `cd ~/projects/qwen3-embed && uv run pytest tests/` + embed smoke | N/A (library) | `pytest exit 0` + smoke returns shape `(1, N)` |
| 22 | web-core | pytest + SearXNG runner | `cd ~/projects/web-core && uv run pytest tests/` + `uv run python -m web_core.searxng.runner --check` | N/A | `pytest exit 0` + "SearXNG ready at http://127.0.0.1:8888" |
| 23 | claude-plugins | jq + lint + dry-run install | `jq . plugins/*/plugin.json` + `node scripts/lint-marketplace.js` + `claude plugin install <name> --dry-run` per MCP | N/A | jq exit 0 + lint exit 0 + dry-run no FAIL |
| 24 | n24q02m profile | markdownlint + linkcheck + secret-scan | `npx markdownlint-cli '**/*.md'` + link-check CLAUDE.md/MEMORY.md + grep for inline secrets | N/A | markdown lint 0 + no broken links + no secret matches |

## 3. Per-Config Procedure (uniform 9 steps for configs #1-20)

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
         - stdio-proxy: skip (cred loaded from config.enc)

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

Configs #21-24 (non-MCP): custom steps per repo — xem `non-mcp-repos.md` chi tiết.

## 4. ALL GREEN Gate

**24/24 PASS bắt buộc** trước khi exit Phase 3. Bất kỳ config nào fail -> **back to Phase 1 (`backlog-clearance.md`)**, không được skip forward hay "fix sau". Root cause fix + re-run scenario (tuân `feedback_fix_root_cause_verify.md`).

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

- **20 MCP configs** × 9 steps uniform + **4 non-MCP configs** × custom steps = **24 total**.
- All MCP configs require user interaction for credential step (except stdio modes reuse prior cred from config.enc — vẫn phải có step [4] state verify).
- Clean state per server **before each config** — bao gồm mode khác nhau của cùng 1 server.
- **NEVER skip to Phase 4 with <24 green.**
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
