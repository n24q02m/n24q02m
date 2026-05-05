# MCP Mode Matrix — Canonical Reference

Tài liệu gốc cho kiến trúc transport mode của 8 MCP server. Fixed 2026-04-18, flip sang full-matrix E2E 2026-04-20, +imagine-mcp 2026-04-24. KHÔNG tự thêm mode, KHÔNG rename, KHÔNG dual-codepath parallel.

## 1. Mode Matrix (8 servers)

| Server | Default (auto-install / recommended manual) | Other supported modes |
|---|---|---|
| **better-notion-mcp** | `http remote oauth` | `http local relay`, `stdio proxy` |
| **better-telegram-mcp** | `http remote relay` | `http local relay`, `stdio proxy` |
| **better-email-mcp** | `http remote relay` | `http local relay`, `stdio proxy` |
| **wet-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **mnemo-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **better-code-review-graph** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **imagine-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **better-godot-mcp** | `http local non-relay` | `stdio proxy` |

"Default" = mode tự động kích hoạt khi user cài plugin (auto-install) + mode recommended khi cài thủ công. Các mode khác = explicit opt-in qua env var / CLI flag. **Không được có mode ngoài bảng này.**

**Post 1-Daemon merge (2026-04-23)**: `http local relay` + `stdio proxy` của server credentialed collapsed thành mode logic `daemon` — 1 backend (`runSmartStdioProxy` TS / `run_smart_stdio_proxy` Python) serve CẢ stdio pipe lẫn HTTP `/mcp` endpoint. Mode matrix giữ nguyên cho rõ ràng entry point; E2E matrix count theo daemon (xem `e2e-full-matrix.md` section 2.5).

## 2. Mode Definitions

### `http remote oauth`
Server deploy remote tại `https://<server>.n24q02m.com` (OCI) hoặc self-host URL. Server act như OAuth 2.1 Resource Server + delegate authentication tới OAuth provider chính (vd Notion OAuth app). User cài plugin -> auto redirect tới provider OAuth login -> callback lưu token per-user -> plugin connect qua Bearer. **Multi-user thật sự**, token isolate theo `JWT sub`. CHỈ áp dụng khi provider support OAuth 2.1 proper. Hiện chỉ notion dùng mode này.

### `http remote relay`
Server deploy remote tại `https://<server>.n24q02m.com` (OCI) hoặc self-host + credential submit qua browser form tại URL relay remote, ECDH encrypt payload, server poll `poll_for_result` từ `mcp-core`. Dùng khi provider KHÔNG có OAuth 2.1 proper (telegram phone/OTP, email IMAP / OAuth device code, v.v.). Multi-user qua per-`JWT sub` credential store.

### `http local relay`
Server chạy LOCAL (`127.0.0.1:<port>`) qua `runLocalServer` (TS) / `run_local_server` (Python) từ `mcp-core`, serve credential form ở `/authorize` endpoint. User paste credential ở browser local. **Không gọi ra internet** cho setup flow. Single-user scope, credential lưu vào `config.enc` qua `write_config/read_config` (`mcp-core`). Dùng cho wet/mnemo/crg (cred đơn giản: API key, OAuth device code local).

### `http local non-relay`
Giống `http local relay` về transport (local 127.0.0.1) nhưng KHÔNG có `relaySchema` và KHÔNG serve credential form. CHỈ godot dùng (game tools không cần API key, không cần cred). Entry point bypass setup flow, start MCP protocol endpoint ngay.

### `stdio proxy`
Server expose stdio transport qua `mcp-stdio-proxy` CLI hoặc entry point riêng (`--stdio` flag hoặc `MCP_TRANSPORT=stdio` env var). Backward compatibility cho agent không support HTTP transport. **BẮT BUỘC mọi server hỗ trợ** (kể cả server có default là HTTP). Proxy internally spawn HTTP local relay rồi bridge stdin/stdout <-> HTTP.

**Fallback rule (BẤT BIẾN)**: Khi stdio khởi động với `config.enc` trống:
1. Đọc `config.enc` qua `resolve_config` / `resolveConfig`.
2. Nếu thiếu cred → spawn **LOCAL HTTP** via `run_local_server` / `runLocalServer` với `relaySchema`, port=0 (random), host=`127.0.0.1`.
3. Print URL local (`http://127.0.0.1:<port>/`), `tryOpenBrowser(url)`.
4. `onCredentialsSaved` callback → `writeConfig(SERVER_NAME, creds)` → schedule `handle.close()` sau 5s grace (cho browser nhận `notifyComplete`).
5. **TUYỆT ĐỐI KHÔNG**: `create_session(remote_url, ...)`, hit `https://<server>.n24q02m.com`, follow default mode (remote-oauth hay remote-relay), advertise deployed domain as paste-key endpoint.

Default mode (remote-oauth / remote-relay) chỉ active khi user explicit chọn HTTP mode qua `MCP_MODE` env var HOẶC cài qua plugin auto-install (Claude Code plugin system). stdio-proxy **độc lập** với default mode — luôn local paste-key form.

## 2.5. Subdomain Deployment Matrix (n24q02m.com)

**Quy tắc BẤT BIẾN**: Chỉ servers có default `http remote *` mới được n24q02m deploy subdomain public. Servers có default `http local *` + optional `(self-host)` = user tự deploy trên infra của họ, n24q02m KHÔNG host public instance.

| Server | Subdomain deployed by n24q02m? | Lý do |
|---|---|---|
| **better-notion-mcp** | ✅ `notion-mcp.n24q02m.com` (Caddy + OCI VM) | Default `http remote oauth` — end-user không self-host notion OAuth app được |
| **better-telegram-mcp** | ✅ `telegram-mcp.n24q02m.com` | Default `http remote relay` — cần multi-user per-JWT-sub |
| **better-email-mcp** | ✅ `email-mcp.n24q02m.com` | Default `http remote relay` — cần multi-user per-JWT-sub |
| **wet-mcp** | ❌ **KHÔNG** | Default `http local relay` — user cài plugin chạy local 127.0.0.1. `(self-host)` = user deploy cho riêng họ, không phải n24q02m |
| **mnemo-mcp** | ❌ **KHÔNG** | Same as wet |
| **better-code-review-graph** | ❌ **KHÔNG** | Same as wet |
| **imagine-mcp** | ❌ **KHÔNG** | Same as wet |
| **better-godot-mcp** | ❌ **KHÔNG** | Default `http local non-relay`, no HTTP remote |

**Semantic của `(self-host)`**: Annotation cạnh tên mode (vd `http remote relay (self-host)`) = **end-user tự deploy instance của chính họ**. Họ point MCP client sang `MCP_RELAY_URL=https://<their-infra>.example.com`. n24q02m **KHÔNG cung cấp** subdomain cho các mode annotated `(self-host)`.

**Kéo theo yêu cầu code**:
1. Server có default local-relay **KHÔNG được hardcode `DEFAULT_RELAY_URL = "https://<server>.n24q02m.com"`**. Hardcode như vậy = assume centralized relay tồn tại, trái matrix.
2. Server có optional `(self-host)` mode phải **require `MCP_RELAY_URL` env var explicit** khi `MCP_MODE=remote-relay` — reject startup nếu missing, kèm error message hướng dẫn user set URL của self-host instance của họ.
3. Server deploy subdomain (notion/telegram/email) có thể baked-in production URL cho client plugin, nhưng phải override-able qua env var để user self-host thay thế.

**Anti-pattern cấm**:
- `DEFAULT_RELAY_URL = "https://wet-mcp.n24q02m.com"` trong wet-mcp/mnemo/crg source code (vi phạm 2026-04-22: tồn tại cả 3, di sản từ thời mcp-relay-core centralize).
- Central relay server route `<server>.n24q02m.com/<server>/` cho tất cả 6 MCP servers (kiến trúc cũ `mcp-relay-core/packages/relay-server` + `pages/{6}`). Đã deprecated 2026-04-22, re-archived.
- Assume subdomain `<server>.n24q02m.com` tồn tại cho bất kỳ server nào có default local-relay — KHÔNG có, và không nên tạo.

## 3. Activation Mechanism

Chọn mode qua env var `MCP_MODE` (ưu tiên) HOẶC CLI flag. Nếu không set -> dùng default theo matrix.

| `MCP_MODE` value | CLI flag equivalent | Áp dụng cho |
|---|---|---|
| `remote-oauth` | `--mode=remote-oauth` | notion default |
| `remote-relay` | `--mode=remote-relay` | telegram, email default; wet/mnemo/crg self-host |
| `local-relay` | `--mode=local-relay` | wet/mnemo/crg default; notion/telegram/email fallback |
| `local-non-relay` | `--mode=local-non-relay` | godot default |
| `stdio-proxy` | `--stdio` hoặc `MCP_TRANSPORT=stdio` | mọi server (backward compat) |

Set sai value -> server PHẢI reject startup với error rõ ràng liệt kê valid modes, KHÔNG silently fallback.

## 4. Anti-patterns (CẤM)

- **Renaming mode**: đổi tên từ `http remote relay` thành `cloud relay` / `hosted relay` / tên khác trong code, docs, entry point, test. Tên phải khớp bảng matrix, không alias.
- **Inventing new mode**: thêm mode không có trong matrix (vd `remote oauth` cho telegram khi provider không có OAuth 2.1, `hybrid mode`, `proxy mode`). Provider thiếu capability -> không hỗ trợ mode đó, không fake.
- **Dual-codepath parallel**: khi default chạy, TUYỆT ĐỐI không activate thêm codepath khác. Vi phạm điển hình: `runLocalServer` serve `/authorize` local form ĐỒNG THỜI lazy-trigger remote relay URL -> user mở plugin thấy 2 URL, không biết paste cred vào cái nào. Phải ONE active codepath per process.
- **Auto-activating non-default mode when default is configured**: nếu user đã setup default (vd notion có OAuth token valid) thì không được tự chuyển sang `local relay` "for fallback". Default stays default. Mode switch CHỈ khi user explicit set `MCP_MODE`.
- **stdio fallback to remote URL**: `create_session(DEFAULT_RELAY_URL="https://<server>.n24q02m.com", RELAY_SCHEMA)` trong stdio lazy trigger. Sai vì: (a) remote URL không luôn serve paste-key, (b) kiến trúc mismatch (notion remote = OAuth, paste-key từ stdio = inconsistent), (c) default mode != stdio fallback. stdio fallback phải **LOCAL HTTP** qua `run_local_server` — xem section `stdio proxy` mục 2.
- **Centralized relay server for all MCP servers** (legacy `mcp-relay-core` pattern): 1 Docker container serve `wet-mcp.n24q02m.com/wet/`, `mnemo-mcp.n24q02m.com/mnemo/`, etc. Đã deprecated 2026-04-22. Mỗi MCP server định nghĩa riêng mode của mình; n24q02m chỉ deploy subdomain cho default-remote servers (xem mục 2.5). KHÔNG xây relay gateway dùng chung.
- **Assume `<server>.n24q02m.com` tồn tại cho mọi server**: audit plan/spec/infra trước khi reference subdomain public. Default local-relay servers (wet/mnemo/crg) KHÔNG có subdomain — ref `feedback_matrix_selfhost_semantics.md`.

## 5. Conformance Verification Checklist

Khi audit một server against matrix entry:

1. **Entry point selects single default codepath**: đọc `src/<repo>/__main__.py` / `src/transports/http.ts` -> verify có đúng 1 branch active theo default matrix, không parallel codepath.
2. **Non-default modes route through mcp-core primitives**: `local relay` dùng `run_local_server` / `runLocalServer`; `remote relay` dùng `create_session` + `poll_for_result`; `remote oauth` dùng mcp-core OAuth 2.1 AS helper. Không duplicate HTTP/Starlette/uvicorn riêng.
3. **No mode outside the matrix supported**: grep `MCP_MODE` values được chấp nhận, verify khớp exactly với các mode cho server đó trong matrix. Giá trị lạ -> divergence.
4. **Default mode auto-activated on install**: `plugin.json` / install script không set `MCP_MODE` -> server phải khởi động đúng default mode. Test: fresh install, không env var, observe mode banner ở stderr.
5. **`stdio proxy` luôn available**: mọi server có entry point `--stdio` hoặc `MCP_TRANSPORT=stdio` start được, proxy chuẩn.
6. **Switching test**: set `MCP_MODE=<each supported mode>` -> verify mode đó start đúng codepath, không regress default.

## 6. Why 2026-04-20 Flip: Full Matrix E2E

Trước 2026-04-20: E2E test CHỈ cover default mode mỗi server (7 configs). Đủ cho MVP ship nhưng miss bug ở non-default modes (vd telegram `local relay` không fallback đúng, email `stdio proxy` leak PID, wet `remote relay` self-host thiếu Bearer middleware).

Từ 2026-04-20: E2E cover **full matrix** = 20 MCP configs (mỗi server x mỗi mode nó hỗ trợ) + 4 non-MCP configs (mcp-core TS/Python lib, qwen3-embed server, web-core shared package, claude-plugins manifest). Mỗi config clean-state test qua relay/OAuth flow thật, không shortcut env var. Chi tiết procedure: xem `e2e-full-matrix.md`. Audit gh commands cho empty-backlog gate: xem `audit-commands.md`.

Rationale: release cascade (mcp-core bump -> 7 MCP bumps) dễ breakage ở non-default modes vì CI green chỉ verify default. User chạy `MCP_MODE=local-relay` trên production server có OAuth config -> gặp bug không ai test. Full matrix E2E trước mỗi stable release cascade ngăn drift giữa modes.

## 7. E2E Matrix Re-classification 2026-04-25 — 16 Configs (3 Axes)

Section 1 trên là **deployment matrix** (8 servers × các mode mỗi server hỗ trợ). Section này là **E2E test matrix** — chiếu xuống 3 axes (auth / interaction / tier) để driver script chạy.

**3 Axes**:
- **Auth flow** (3 values): `none` / `oauth` / `relay`. Chỉ notion remote dùng `oauth` (delegated upstream Notion OAuth + DCR). Tất cả relay/device-code/OTP đều quy về `relay`.
- **Interaction**: `non-interaction` (driver fill xong, no upstream gate) / `interaction` (driver fill xong, user click upstream gate).
- **Tier**: `T0` (precommit + CI auto) / `T2` (local manual `make e2e-full`).

**Multi-user là DEPLOYMENT PROPERTY của remote mode** — KHÔNG phải config test riêng. Test isolation 1 lần ở mcp-core fixture (concurrent 2-user, JWT sub separation), smoke test per-server.

### 16 Configs

**T0-only (5)** — CI/precommit, no upstream:
1. mcp-core CI (unit + integration)
2. qwen3-embed CI (Modal worker tests)
3. web-core CI (build + lint)
4. claude-plugins CI (skill validation)
5. better-godot-mcp stub mode (no exe)

**T2 non-interaction (6)** — driver pre-fills relay form, tools active no gate:

| # | Server | Auth | Test ở |
|---|---|---|---|
| 6 | better-notion-mcp (paste integration token) | relay | local |
| 7 | better-email-mcp Gmail (paste app password) | relay | local + remote |
| 8 | better-telegram-mcp bot (paste bot token) | relay | local + remote |
| 9 | better-code-review-graph (paste optional cloud keys) | relay | local + remote |
| 10 | imagine-mcp (paste LLM provider keys) | relay | local + remote |
| 11 | better-godot-mcp with-exe (auto-detect PATH) | none | local |

**T2 interaction (5)** — driver fills, user clicks upstream gate:

| # | Server | Auth | Test ở | User gate |
|---|---|---|---|---|
| 12 | better-notion-mcp delegated-oauth | **oauth** | remote | Click Notion consent |
| 13 | better-email-mcp Outlook | relay + device-code | local + remote | Click Microsoft device-code |
| 14 | better-telegram-mcp user mode | relay + OTP + 2FA | local + remote | Type OTP + 2FA password |
| 15 | wet-mcp (sync mandatory) | relay + GDrive device-code | local + remote | Click GDrive device-code |
| 16 | mnemo-mcp (sync mandatory) | relay + GDrive device-code | local + remote | Click GDrive device-code |

### Anti-patterns mới (CẤM)

- **Tách `local-bot` + `remote-bot` thành 2 configs** cho cùng pattern auth. Bot mode pattern giống nhau ở local + remote, multi-user là property → 1 config "test ở local + remote".
- **Tách `wet-no-sync` + `wet-with-sync`** — sync mandatory cho wet/mnemo (`sync_enabled: bool = True`), KHÔNG có "no-sync" mode test.
- **Gọi device-code / OTP / 2FA là "auth mode"** — chúng là post-paste user gates trong relay flow, không phải auth modes riêng.
- **Đếm "delegated-oauth-app" pattern là 1 mode user-facing** — đó là mcp-core internal serving relay/oauth, không tách config.
- **Test multi-user như 1 config riêng** — multi-user là deployment property của remote, test isolation 1 lần ở mcp-core fixture.

### Skret namespace (per-server, best-practice)

```
/<server>-mcp/prod/MCP_DCR_SERVER_SECRET   # per-server JWT signing key
/<server>-mcp/prod/<dynamic-creds>         # user-provided secrets
```

Per-server thay vì shared 1 secret cho 7 MCPs: JWT signing key độc lập (compromise isolation), independent rotation cadence.

**Spec + plan canonical**: `.superpower/mcp-core/{specs,plans}/2026-04-25-e2e-framework-and-multi-user-migration.md`.
