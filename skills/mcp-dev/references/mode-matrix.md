# MCP Mode Matrix — Canonical Reference

Tài liệu gốc cho kiến trúc transport mode của 7 MCP server. Fixed 2026-04-18, flip sang full-matrix E2E 2026-04-20. KHÔNG tự thêm mode, KHÔNG rename, KHÔNG dual-codepath parallel.

## 1. Mode Matrix (7 servers)

| Server | Default (auto-install / recommended manual) | Other supported modes |
|---|---|---|
| **better-notion-mcp** | `http remote oauth` | `http local relay`, `stdio proxy` |
| **better-telegram-mcp** | `http remote relay` | `http local relay`, `stdio proxy` |
| **better-email-mcp** | `http remote relay` | `http local relay`, `stdio proxy` |
| **wet-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **mnemo-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **better-code-review-graph** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **better-godot-mcp** | `http local non-relay` | `stdio proxy` |

"Default" = mode tự động kích hoạt khi user cài plugin (auto-install) + mode recommended khi cài thủ công. Các mode khác = explicit opt-in qua env var / CLI flag. **Không được có mode ngoài bảng này.**

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
