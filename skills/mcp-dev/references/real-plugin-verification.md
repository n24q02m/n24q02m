# Real Plugin Verification (Claude Code, không protocol-only)

## Bối cảnh

E2E driver (`mcp-core/scripts/e2e/`) test giao thức MCP qua HTTP với JWT từ lock file. Đó là **integration test ở mức transport**, KHÔNG thay thế việc verify plugin chạy thật trong Claude Code. Nhiều bug chỉ lộ ra khi plugin chạy thật:

- /mcp UI trên Windows freeze
- Stdio-proxy spawn daemon nhưng URL relay bị giấu trong `~/daemon_stderr.log`
- `_share_cloud_keys_to_peers` mask trạng thái "no creds" của peer
- Stale lock files tích lũy → spawn loop / fork bomb
- Cached compiled JS (npx) lệch version với mcp-core source
- Multiple daemon cho cùng 1 server name (bug lifecycle)
- Bridge eager-open + daemon eager-open spawn 2-3 browser tabs per cycle, respawn loop = spam vô tận (D18 regression 2026-04-29)

## 0. Pre-recommend gate sau P0 rollback (2026-04-29)

Khi prior version vừa ship P0 regression user-facing (browser spam, daemon respawn loop, infinite tab open, machine restart required) và rollback PR đang chuẩn bị release:

BẮT BUỘC stage local-test trước khi recommend user re-enable plugin trong settings.json:

1. Standalone spawn server (`uv run <server>` hoặc `node bin/cli.mjs`) với rollback build mới — KHÔNG qua Claude Code (plugin còn disabled).
2. Verify failure mode regression NOT reachable: e.g. count browser tabs opened (`pgrep -f "https://"` trên macOS, `Get-Process` trên Windows), count daemon process (`ps aux | grep <server>` chỉ 1 entry), count lock files trong session dir.
3. Monitor 5 phút: respawn-loop check. Nếu daemon spawn → die → spawn lại → reproduce P0.
4. Document evidence (process count + tab count + lock count + 5-min monitor log) trong session message.
5. CHỈ sau khi 4 bước trên PASS → instruct user update marketplace mirror + re-enable plugin + restart Claude Code.

Pattern cấm: "release v1.11.4 fix done, anh re-enable + restart Claude Code + verify" — nếu verify fail user sẽ trải qua P0 spam lần 2. Verify trên local trước, recommend sau.

## 4 yêu cầu verify thực tế cho mỗi MCP server

Khi user yêu cầu "verify plugin/MCP trên Claude Code" (test thực tế, không E2E driver), BẮT BUỘC làm đủ 4 bước theo thứ tự:

### 0. Verify mcp-core version match (Step 0, 2026-04-30)

`uvx`/`npx` cache pin transitive deps khi install (xem `feedback_uvx_cache_transitive_pin.md` + `feedback_npx_cache_transitive_pin.md`). Sau core release, plugin local có thể vẫn pin core cũ → silent staleness.

BẮT BUỘC check trước Step 1:

```bash
# Python plugins (uvx-installed)
for srv in better-telegram-mcp wet-mcp mnemo-mcp better-code-review-graph imagine-mcp; do
  ls -d ~/AppData/Roaming/uv/tools/$srv/Lib/site-packages/n24q02m_mcp_core-* 2>/dev/null
done
# Expected: ALL show n24q02m_mcp_core-<latest_published>.dist-info

# TS plugins (npx-cached)
for srv in better-notion-mcp better-email-mcp; do
  for hash in ~/scoop/persist/nodejs24/cache/_npx/*/; do
    grep -l "@n24q02m/$srv" "$hash/package.json" 2>/dev/null && \
      grep -oE '"@n24q02m/mcp-core":\s*"[^"]+"' "$hash/package-lock.json" 2>/dev/null
  done
done
# Expected: mcp-core pin matches latest published
```

Nếu mismatch → `uv tool upgrade --reinstall <plugin>` × 5 + `rm -rf ~/scoop/persist/nodejs24/cache/_npx/<hash>` cho TS. Verify lại trước khi tiếp tục Step 1-4.

### 1. Verify secret saved

- `read_config(server_name)` trả đúng key đã user paste qua relay form.
- Inspect bằng:
  ```python
  from mcp_core.storage.config_file import read_config
  for srv in [...]: print(srv, list(read_config(srv).keys()) if read_config(srv) else 'NONE')
  ```
- Nếu user setup OAuth (GDrive/Microsoft/Notion OAuth), check token file: `~/.<server>/tokens/<provider>.json` hoặc tương đương per server (xem `secrets-skret.md`).
- Nếu server có `_share_cloud_keys_to_peers`, verify cả config của peer (wet/mnemo/crg share cloud keys).

### 2. Verify tool/action call **trong Claude Code**

- KHÔNG dùng MCP protocol-level test (httpx POST tới `/mcp` endpoint với JWT từ lock file). Đó là transport check, KHÔNG phải plugin verification.
- BẮT BUỘC gọi tool qua Claude Code MCP harness:
  - Tool đã loaded → invoke trực tiếp `mcp__plugin_<plugin>_<server>__<tool>` (e.g. `mcp__plugin_wet-mcp_wet__config`).
  - Tool ở deferred list → `ToolSearch` với `select:<full-name>` để load schema, rồi invoke.
  - Tool không xuất hiện ở cả 2 → plugin chưa connect, báo user reload.

#### 2a. Bắt buộc gọi DOMAIN tool có ý nghĩa (KHÔNG help/status)

`__help`, `__config(action='status')`, `__config__open_relay` là metadata tool — pass cả khi domain tier (creds + upstream API) hoàn toàn broken. **Verifying chỉ những tool này = sloppy verify** (vi phạm 2026-04-30 verify-mcp-tool-dispatch).

Mỗi server BẮT BUỘC gọi ≥1 DOMAIN tool có upstream call thật. Bảng chuẩn:

| Server | Domain tool meaningful | Expected result |
|---|---|---|
| `wet-mcp` | `search(query='claude opus 4.7')` | hits với URL + snippet |
| `mnemo-mcp` | `remember(...)` rồi `recall(...)` | id + retrieved text |
| `better-code-review-graph` | `semantic_search_nodes_tool(query='...')` | node list với file paths |
| `imagine-mcp` | `image_describe(url=...)` real image | description text |
| `better-telegram-mcp` | `messages(action='send', chat=..., text=...)` test channel | message id |
| `better-notion-mcp` | `pages(action='list', database_id=...)` hoặc `databases(action='query', ...)` | page titles |
| `better-email-mcp` | `messages(action='list', folder='INBOX')` | from/subject/date list |
| `better-godot-mcp` | `scenes(action='list')` hoặc `nodes(action='get_tree')` open project | scene paths / node tree |

#### 2b. Evidence table BẮT BUỘC trong transcript

Trước khi mark Test B PASS, viết evidence table:

```
| Server | Tool | Input excerpt | Result excerpt | PASS/FAIL |
|---|---|---|---|---|
| wet-mcp | search | query='claude opus 4.7' | "Anthropic announced Claude Opus 4.7..." | PASS |
| ... | ... | ... | ... | ... |
```

Nếu 1/8 FAIL → cả Test B FAIL → root cause investigation. KHÔNG ship "7/8 PASS, ship anyway". Xem memory `feedback_real_plugin_test_strict.md`.

### 3. Verify exactly 1 daemon per server

- `~/.config/mcp/locks/<server>-*.lock` chỉ được có **1 file alive duy nhất** per server name.
- Stale lock detection: `socket.connect(('127.0.0.1', port))` — nếu connect được = alive, nếu không = dead.
- Nhiều stale lock = bug lifecycle (smart_stdio_proxy spawn duplicate, hoặc daemon không cleanup khi exit). Cleanup script:
  ```python
  import socket
  from pathlib import Path
  for lk in Path.home().joinpath('.config/mcp/locks').glob('*.lock'):
      port = int(lk.stem.split('-')[-1])
      try:
          s = socket.socket(); s.settimeout(0.3); s.connect(('127.0.0.1', port)); s.close()
      except: lk.unlink()
  ```
- Nếu vẫn còn duplicate alive sau cleanup → root cause bug, fix mcp-core lifecycle.

### 4. Verify single-user vs multi-user mode

Áp dụng cho server có cả 2 modes (xem `mode-matrix.md`):

- **Single-user (local-relay default)**:
  - `PUBLIC_URL` không set
  - Daemon bind `127.0.0.1`, single shared `config.enc`
  - Verify: 1 user pastes creds → tool call uses those creds.
- **Multi-user (remote-relay với PUBLIC_URL + MCP_DCR_SERVER_SECRET)**:
  - `PUBLIC_URL` set → daemon bind `0.0.0.0:8080`
  - `MCP_DCR_SERVER_SECRET` BẮT BUỘC (xem `feedback_remote_relay_multi_user_enforcement.md`)
  - Per-JWT-sub credential isolation: `~/.<server>/subs/<sub>/tokens/<provider>.json`
  - Verify: 2 different JWT sub UUIDs → 2 separate config entries → tool calls scoped per sub (no cred leak).
- Server nào support cả 2: wet, mnemo, crg, imagine, notion, email, telegram (xem matrix).
- Server chỉ single-user: godot (no creds at all).

## Anti-patterns (không được làm)

- **Mark "verified" chỉ vì E2E driver pass**: driver test transport + form, KHÔNG test plugin trong Claude Code.
- **Mark "verified" chỉ vì daemon connect xanh trong /mcp UI**: UI green = daemon serves /mcp + JWT auth OK, KHÔNG nghĩa là tool gọi được hoặc creds hoạt động.
- **Skip "1 daemon check"**: 1 server có 11 lock files = bug lifecycle. Phát hiện 2026-04-28: wet-mcp tích lũy 11 stale locks vì smart_stdio_proxy spawn liên tục mỗi lần Claude Code restart trong 1 session.
- **Skip multi-user check khi server support**: wet/mnemo/crg đều support nhưng phần lớn deploy single-user; multi-user gap là bug security (cred leak across users) thường bị miss.

## Vi phạm 2026-04-28

User yêu cầu "verify 4 cái đã hoạt động" sau khi config xong relay; em chỉ test protocol-level qua httpx POST với JWT từ lock file, KHÔNG gọi tool qua Claude Code. User pushback: "Yêu cầu gọi tool/action ở đây là gọi trong claude code chứ không phải gọi protocol ở ngoài như lúc trước test!". Đồng thời thiếu "1 daemon check" và "single/multi user check". Đã save thành rule này để session sau không tái phạm.
