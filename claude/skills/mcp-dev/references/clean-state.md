# Clean State — Per-Server E2E Pre-Launch Protocol

**Phase 2 of mcp-dev cascade.** Executed BEFORE every E2E run cho từng config trong `e2e-full-matrix.md`. Purpose: ensure relay flow is exercised **end-to-end** (not skipped because server "already configured from previous session").

Rule gốc: `feedback_e2e_clean_state_all_servers.md` + `feedback_full_live_test.md`.

## 1. Core Rule (BẤT BIẾN)

BẮT BUỘC clean state cho MỌI server TRƯỚC KHI test, không có exception. Kể cả khi server đã configured trong session trước, hoặc đã test server đó trong config khác cùng session.

**Why**: Mục đích E2E là verify relay session creation + browser form submission + server-side config saving + browser success landing. Skip phase 1 vì "đã configured" → bỏ qua phần quan trọng nhất. Vi phạm 2026-04-18 email-mcp: thấy `Found saved OAuth2 tokens for <user-email>` → skip relay → user scold.

## 2. Per-Server Clean Paths

| Server | config.enc entry | Token cache | Session lock (Windows) | Session lock (Linux) |
|---|---|---|---|---|
| better-notion-mcp | key `notion` in `$APPDATA/mcp/config.enc` | N/A (OAuth tokens stored inside config.enc) | `$LOCALAPPDATA/mcp/relay-session-notion.lock` | `~/.cache/mcp/relay-session-notion.lock` |
| better-email-mcp | key `email` in `$APPDATA/mcp/config.enc` | `~/.better-email-mcp/tokens.json` | `$LOCALAPPDATA/mcp/relay-session-email.lock` | `~/.cache/mcp/relay-session-email.lock` |
| better-telegram-mcp | key `telegram` in `$LOCALAPPDATA/mcp/config.enc` | `~/.better-telegram-mcp/*.session` (telethon SQLite) | `$LOCALAPPDATA/mcp/relay-session-telegram.lock` | `~/.cache/mcp/relay-session-telegram.lock` |
| wet-mcp | key `wet` in `$LOCALAPPDATA/mcp/config.enc` | `~/.wet-mcp/tokens/` (GDrive sync only) | `$LOCALAPPDATA/mcp/relay-session-wet.lock` | `~/.cache/mcp/relay-session-wet.lock` |
| mnemo-mcp | key `mnemo` in `$LOCALAPPDATA/mcp/config.enc` | N/A (local SQLite only, no remote tokens) | `$LOCALAPPDATA/mcp/relay-session-mnemo.lock` | `~/.cache/mcp/relay-session-mnemo.lock` |
| better-code-review-graph | key `crg` in `$LOCALAPPDATA/mcp/config.enc` | N/A (local SQLite only) | `$LOCALAPPDATA/mcp/relay-session-crg.lock` | `~/.cache/mcp/relay-session-crg.lock` |
| better-godot-mcp | N/A (no credentials) | N/A | N/A | N/A |

### NOTE: config.enc cross-language drift

- **TypeScript servers** (notion, email, godot) dùng `$APPDATA/mcp/config.enc` — theo `env-paths` npm package convention.
- **Python servers** (telegram, wet, mnemo, crg) dùng `$LOCALAPPDATA/mcp/config.enc` — theo `platformdirs` convention.
- Known parity issue: `feedback_mcp_config_parity.md`. Clean script PHẢI xoá cả 2 paths để tránh leak state cross-language.

## 3. Clean State Bash Function

Script dưới đây (Windows Git Bash; adapts to Linux qua `$HOME/.cache/mcp/` fallback). Save ra `~/projects/mcp-e2e/clean-state.sh` rồi `source` vào test runner.

```bash
#!/usr/bin/env bash
# clean-state.sh -- per-server clean state before E2E run
# Usage: source clean-state.sh; clean_state notion

clean_state() {
  local server=$1

  if [[ -z "$server" ]]; then
    echo "Usage: clean_state <server>" >&2
    return 1
  fi

  echo ">>> Cleaning state for $server..."

  # 1. Remove server entry from config.enc (both TS + Python paths)
  if command -v mcp-core-cli &>/dev/null; then
    mcp-core-cli config delete "$server" 2>/dev/null || true
  else
    # Fallback via Python mcp-core primitive
    python -c "
try:
    from mcp_core.storage.config_file import delete_config
    delete_config('$server')
    print(f'  config.enc: removed entry for $server')
except Exception as e:
    print(f'  config.enc: skipped ({e})')
" 2>/dev/null
  fi

  # 2. Remove server-specific token cache
  case "$server" in
    email)
      rm -rf ~/.better-email-mcp/tokens.json 2>/dev/null
      echo "  token cache: removed ~/.better-email-mcp/tokens.json"
      ;;
    telegram)
      rm -rf ~/.better-telegram-mcp/*.session 2>/dev/null
      rm -rf ~/.better-telegram-mcp/*.session-journal 2>/dev/null
      echo "  token cache: removed ~/.better-telegram-mcp/*.session"
      ;;
    wet)
      rm -rf ~/.wet-mcp/tokens/ 2>/dev/null
      echo "  token cache: removed ~/.wet-mcp/tokens/"
      ;;
    notion|mnemo|crg|godot)
      # No separate token cache
      ;;
  esac

  # 3. Remove session lock
  local lock_dir
  if [[ -n "${LOCALAPPDATA:-}" ]]; then
    lock_dir="$LOCALAPPDATA/mcp"
  else
    lock_dir="$HOME/.cache/mcp"
  fi
  rm -f "$lock_dir/relay-session-$server.lock"
  echo "  session lock: removed $lock_dir/relay-session-$server.lock"

  echo ">>> Clean complete for $server"
}

clean_all() {
  for server in notion email telegram wet mnemo crg godot; do
    clean_state "$server"
  done
}
```

## 4. Nuclear Option (khi per-entry cleanup fails)

Dùng khi nghi ngờ state leak hoặc mcp-core `delete_config` không hoạt động (vd corrupted config.enc, locked file). Xoá SẠCH toàn bộ state MCP:

```bash
# Removes WHOLE config.enc across both TS + Python paths
rm -f "$APPDATA/mcp/config.enc" "$LOCALAPPDATA/mcp/config.enc"

# Remove ALL session locks
rm -rf "$LOCALAPPDATA/mcp/relay-session-"*.lock "$HOME/.cache/mcp/relay-session-"*.lock

# Remove ALL server-specific token caches
rm -rf ~/.better-email-mcp/ ~/.better-telegram-mcp/ ~/.wet-mcp/tokens/
```

Sau nuclear: chạy lại `clean_all` để confirm + verify relay URL xuất hiện khi launch.

## 5. Verification After Clean

Cho mỗi server (bất kể clean mode dùng `clean_state` hay nuclear), verify 3 điểm TRƯỚC KHI proceed to Phase 3:

1. **Launch server** → relay URL PHẢI xuất hiện ở stderr. Nếu không → state chưa clean, quay lại nuclear.
2. **Browser form accessible + empty** → mở relay URL, form render, KHÔNG có pre-filled credentials (email, token, API key fields empty).
3. **MCP `config(status)` tool** → return `state=unconfigured` (hoặc equivalent initial state).

Chỉ khi cả 3 ✓ mới proceed Phase 3 (browser submit + server config save + tool call verify).

## 6. Common Pitfalls

- **"Already configured, skip"** → defeats purpose of E2E. Phase 1 relay setup CHÍNH LÀ cái cần test.
- **Cleaning only config.enc but leaving token cache** → email/telegram/wet server reuses cached OAuth/session tokens → relay URL không xuất hiện.
- **Cleaning only Python `$LOCALAPPDATA` but not TypeScript `$APPDATA`** (hoặc ngược lại) → leaks state cross-language. PHẢI xoá cả 2.
- **Not killing running server process** → old process holds cached state trong memory (OAuth token, session lock file descriptor). Luôn `taskkill /F /IM node.exe` hoặc `pkill -f mcp` trước `clean_state`.
- **Cleaning giữa các configs cùng server** → nếu matrix test stdio + http + remote cùng 1 server, PHẢI clean giữa mỗi config (không chỉ giữa servers).
- **Relay session lock file hold-over** → Git Bash sometimes fails `rm` trên `.lock` file locked bởi previous process. Kill process trước.

## 7. Rule for Phase 3 Entry

Cho mỗi một trong **20 MCP configs** trong `e2e-full-matrix.md`, chạy `clean_state <server>` TRƯỚC KHI launch config đó. Không exception.

Template loop:

```bash
source clean-state.sh

for config in $(cat e2e-matrix.txt); do
  server=$(echo "$config" | cut -d: -f1)  # e.g. "notion:http-remote-oauth"
  clean_state "$server"
  ./run-config.sh "$config"
done
```

Nếu test 1 server ở N configs khác nhau (vd notion stdio + http local + http remote) → clean N lần, 1 lần trước mỗi config launch.

## 8. Cross-References

- `e2e-full-matrix.md` — 20 MCP configs + 4 non-MCP, sử dụng protocol này pre-launch.
- `relay-flow.md` — luồng relay identical local-relay ≡ remote-relay, verify sau clean.
- `mode-matrix.md` — xác định server nào cần clean những token cache gì.
- `config-parity.md` — lý do tại sao phải xoá cả `$APPDATA` + `$LOCALAPPDATA`.
- `feedback_e2e_clean_state_all_servers.md` — incident context gốc.
- `feedback_full_live_test.md` — anti-pattern "inject env var bypass relay".
