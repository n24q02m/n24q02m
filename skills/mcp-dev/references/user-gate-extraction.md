# Extract User Gate URL/Code from Driver Log

BẮT BUỘC pattern khi run E2E user_gate config (browser-form / device-code / oauth-redirect).

## 4-step pattern

1. **Spawn driver với `tee /tmp/<config>.log`** — KHÔNG `| tail -N` (buffer never flushes mid-run)
2. **Poll log 60-120s grep URL hoặc user_code**:
   - browser-form: `http://127.0.0.1:<port>/authorize?...`
   - device-code: `https://www.google.com/device` hoặc `https://microsoft.com/devicelogin` + `User code: XXX-XXX-XXX`
   - oauth-redirect: authorization URL với state + PKCE
3. **Paste vào response cho user** với markdown emphasis: header `# ⚠️ <CONFIG>` + URL trong code block + code in `**` emphasis
4. **Sau user complete → driver poll** → nếu config có matrix `local` + `remote` → repeat extraction cho iteration sau

## Anti-patterns CẤM

- "Khi browser hoặc terminal hỏi OTP, anh paste vào"
- "Driver đang đợi, anh xem terminal"
- "Browser tự mở"

User KHÔNG thấy terminal (Claude Code own), KHÔNG biết URL nào. Driver poll output bị buffer through `| tail -N` → 0 bytes file, user nothing.

## Violation

525c9518 + 2026-04-30 session 2d88d796 USER L3037 — em đã làm sai pattern này nhiều session liên tiếp.

Memory: `feedback_extract_user_gate_url_code.md`.
