# Reuse mcp-core Primitives — Bắt Buộc

## 1. Core principle

Mọi MCP server trong scope (wet, mnemo, crg, better-notion, better-email, better-telegram, better-godot, cùng bất kỳ server mới nào như imagine-mcp) **PHẢI tối đa hoá reuse** các primitive từ:

- Python: `n24q02m-mcp-core` (package `mcp_core`)
- TypeScript: `@n24q02m/mcp-core`

**Không duplicate** logic đã tồn tại trong mcp-core. Không copy-paste, không re-implement "tương đương", không "viết lại cho đơn giản". Duplicate primitive = drift cross-language + cross-repo + khó maintain + bug khác nhau giữa các server (case study ở section 7).

Nếu cần 1 primitive mà mcp-core chưa có → **contribute upstream TRƯỚC**, release mcp-core version mới, rồi mới consume (xem section 3).

## 2. Primitives table

Bảng dưới là primitives đã có parity Python + TypeScript trong `mcp-core` (verified 2026-04-20).

| Primitive | Python import | TS import | Purpose |
|---|---|---|---|
| Config storage | `from mcp_core.storage.config_file import write_config, read_config, delete_config` | `import { writeConfig, readConfig, deleteConfig } from "@n24q02m/mcp-core/storage"` | Platform-agnostic encrypted config (respects APPDATA on Windows, XDG on Linux/macOS) |
| Session lock | `from mcp_core.storage.session_lock import acquire_session_lock, release_session_lock, write_session_lock` | `import { acquireSessionLock, releaseSessionLock } from "@n24q02m/mcp-core/storage"` | Parallel-process safety cho relay session (tránh 2 instance cùng launch relay) |
| Relay client | `from mcp_core.relay.client import create_session, poll_for_result, send_message` | `import { createSession, pollForResult, sendMessage } from "@n24q02m/mcp-core/relay"` | HTTP client đến relay server (ECDH handshake + long-poll result) |
| OAuth 2.1 AS | `from mcp_core.transport.local_server import run_local_server, build_local_app` | `import { runLocalServer } from "@n24q02m/mcp-core/transport"` | Local Starlette/uvicorn (Python) hoặc Hono (TS) serving `/authorize` form + OAuth AS endpoints |
| Browser open | `from mcp_core.relay.browser import try_open_browser` | `import { tryOpenBrowser } from "@n24q02m/mcp-core/relay"` | Cross-platform browser launcher (Windows rundll32, WSL `powershell.exe`, macOS `open`, Linux `xdg-open`) |
| Credential state | `from mcp_core.auth.credential_form import render_credential_form` + schema từ `mcp_core.schema` | `import { renderCredentialForm } from "@n24q02m/mcp-core/auth"` + schema từ `@n24q02m/mcp-core/schema` | Multi-step credential flow (OTP, 2FA, Device Code chain), state machine |
| Encryption (ECDH + AES) | `from mcp_core.crypto.ecdh import ...` + `from mcp_core.crypto.aes import ...` | `import { ... } from "@n24q02m/mcp-core/crypto"` | Browser-to-server credential encryption (ECDH key exchange + AES-GCM) |
| HTTP transport | `from mcp_core.transport.streamable_http import StreamableHTTPServer` + `OAuthMiddleware` | `import { StreamableHTTPServer } from "@n24q02m/mcp-core/transport"` | HTTP transport với OAuth Bearer middleware cho `/mcp` endpoint |
| Well-known metadata | `from mcp_core.auth.well_known import authorization_server_metadata, protected_resource_metadata` | `import { authorizationServerMetadata, protectedResourceMetadata } from "@n24q02m/mcp-core/auth"` | OAuth 2.1 `.well-known/oauth-authorization-server` + `.well-known/oauth-protected-resource` |

**Lưu ý naming**: Python dùng `snake_case`, TS dùng `camelCase`. Tên primitive + signature ngữ nghĩa ĐỒNG NHẤT cross-language — nếu thấy lệch (vd Python có `poll_for_result` nhưng TS không có `pollForResult`) → bug parity, report lên mcp-core.

## 3. Add-primitive protocol

Khi viết MCP server và phát hiện mcp-core THIẾU primitive mình cần:

1. **Step 1 — Contribute upstream FIRST**: mở PR vào `n24q02m/mcp-core`:
   - Add implementation vào `packages/core-py/src/mcp_core/<module>/`
   - Add parity implementation vào `packages/core-ts/src/<module>/`
   - Add parity tests (cross-language test vectors: cùng input → cùng output bytes/JSON)
   - Export từ `packages/core-py/src/mcp_core/<module>/__init__.py` + `packages/core-ts/src/index.ts`
   - Update `CHANGELOG.md` + bump version (PSR tự tính từ commit prefix `feat:`)
2. **Step 2 — Release mới**: merge PR → CD chạy semantic-release → publish `n24q02m-mcp-core` lên PyPI + `@n24q02m/mcp-core` lên npm/Bun registry. CD workflow tự động tạo tracking issue ở downstream repo (xem rule `CORE RELEASE → AUTO-ISSUE DOWNSTREAM`).
3. **Step 3 — Consume từ MCP server**: bump mcp-core dependency trong `pyproject.toml` / `package.json`, import primitive, dùng.

**TUYỆT ĐỐI KHÔNG** copy-paste implementation vào MCP server "tạm thời rồi migrate sau". Tạm thời = vĩnh viễn. Duplicate primitive đã xảy ra với:
- `try_open_browser` trong 4 server (better-email, better-notion, wet, mnemo) → consolidation deferred to post-M cleanup
- `credential-state.ts` trong better-email-mcp + OAuth device trigger trong better-notion-mcp → drift, fix khác nhau

## 4. Parity requirement

Mỗi primitive trong mcp-core **BẮT BUỘC** có cả 2 bản:
- Python trong `packages/core-py/src/mcp_core/`
- TypeScript trong `packages/core-ts/src/`

Cross-language test vectors bắt buộc:
- Cùng input → cùng output (byte-exact cho crypto, field-exact cho config/schema)
- Test case trong `packages/core-py/tests/test_<module>.py` + `packages/core-ts/src/<module>/__tests__/<module>.test.ts` dùng chung fixture JSON ở `packages/test-vectors/`
- Ví dụ: ECDH handshake Python encrypt → TS decrypt thành công, và ngược lại

Vi phạm parity → bug cross-language (case study: config storage path Python dùng `platformdirs` với $LOCALAPPDATA, TS dùng `env-paths` với $APPDATA → 2 server ghi vào 2 folder khác nhau trên Windows → config "biến mất" khi switch implementation).

## 5. Bug fix protocol cho primitive

Khi phát hiện bug trong 1 primitive mcp-core (bất kể do E2E test, user report, hay audit):

1. Fix trong **CẢ** `core-py` **VÀ** `core-ts` — 1 PR duy nhất
2. Update parity test vectors nếu behavior có thay đổi (thêm test case reproduce bug, verify cả 2 bản đều fix)
3. Cover regression cho TẤT CẢ server consuming (grep usage trước khi merge)
4. Bump mcp-core version → cascade bump xuống downstream repo

**KHÔNG BAO GIỜ** fix 1 language only với lý do "TS không bị bug đó" hay "Python chưa cần". Parity drift = kỹ thuật debt cascade xuống mọi downstream repo.

## 6. Platform differences caveat

mcp-core handle platform differences internally. MCP server **KHÔNG** được hardcode path hay platform-specific command:

| Concern | Sai (hardcode trong MCP server) | Đúng (gọi mcp-core) |
|---|---|---|
| Config path | `os.path.expandvars("$APPDATA/mcp/config.enc")` | `write_config(server_name, {...})` |
| Browser launch Windows | `subprocess.run(["rundll32", "url.dll,FileProtocolHandler", url])` | `try_open_browser(url)` |
| Browser launch WSL | `subprocess.run(["powershell.exe", "-c", f"Start-Process {url}"])` | `try_open_browser(url)` (tự detect WSL) |
| Free port | custom `socket.bind(('', 0))` loop | `find_free_port()` từ `mcp_core.transport.local_server` |
| Session lock path | `tempfile.gettempdir() + "/mcp/lock-foo"` | `acquire_session_lock("foo")` |

Mọi platform branching (Windows/macOS/Linux/WSL) đã được centralize trong mcp-core. Nếu thấy branching logic lặp lại trong MCP server → refactor dùng primitive hoặc contribute primitive mới lên core.

## 7. Case study (2026-04-18)

**Bug**: better-notion-mcp + better-email-mcp (TS) báo "Setup complete" nhưng MCP connect fail, khác hẳn với Python counterparts (better-notion-mcp Python + better-email-mcp Python) "Setup complete" + connect OK.

**Root cause audit**:
1. Config storage — core-py dùng `platformdirs` ghi vào `$LOCALAPPDATA/mcp/config.enc` (Windows), core-ts dùng `env-paths` ghi vào `$APPDATA/mcp/config.enc`. 2 path khác nhau trên Windows → server restart đọc nhầm folder → config "biến mất".
2. `relay-setup.ts` trong better-email-mcp có duplicate OAuth device trigger khác với `setup.py` Python — core-ts parity thiếu primitive `trigger_oauth_device_flow`, TS tự implement → behavior drift.
3. `credential-state.ts` trong better-email-mcp duplicate state machine khác với Python `CredentialState` → 2 enum values khác nhau.

**Fix**:
1. Consolidate config storage path trong mcp-core: cả Python + TS dùng chung algorithm `$APPDATA` Windows / `$XDG_CONFIG_HOME` Linux / `~/Library/Application Support` macOS, verify byte-exact cross-language test vector.
2. Add `trigger_device_flow` primitive vào cả core-py + core-ts với parity test, replace duplicated logic trong better-email-mcp TS.
3. Move `CredentialState` enum + `resolve_credential_state` function vào mcp-core, single source of truth cho cả 7 server.

**Lesson**: Audit mọi primitive usage cross-repo TRƯỚC KHI ship stable release. Nếu 1 primitive chỉ tồn tại trong 1 language → đó là drift, KHÔNG phải design choice.
