# Relay Flow — Local ≡ Remote UI Parity + Credential State Machine

Reference cho việc implement/audit `http local-relay` + `http remote-relay` trong CÙNG MCP server (email/telegram/wet/mnemo/crg). Rule này áp dụng khi 1 server support **cả 2 modes**, không áp dụng cross-category (notion remote-oauth khác, godot local-non-relay khác).

## 1. Parity Rule (BẤT BIẾN)

Nếu server support **cả** `http local-relay` VÀ `http remote-relay`, UI + luồng credential PHẢI **identical**. User mở relay URL ở 2 modes PHẢI thấy cùng form, cùng fields, cùng providers, cùng validation, cùng success landing. Khác biệt **duy nhất** nằm ở tầng storage + auth, KHÔNG nằm ở UX.

"Identical" nghĩa là: field count, labels, types, placeholders, helpText, multi-step triggers, error messages, success screens, polling behavior — tất cả ≡.

## 2. Allowed Differences (CHỈ 3)

1. **Storage scope**
   - `local-relay`: single-user → `writeConfig(server, creds)` ghi vào `config.enc` (platformdirs path).
   - `remote-relay`: multi-user → `perUserTokenStore.save(sub, creds)` keyed by JWT `sub` claim.

2. **OAuth 2.1 AS endpoints** (remote ONLY)
   - `/authorize` (credential form UI)
   - `/token` (JWT issuance sau khi creds saved)
   - `/.well-known/oauth-authorization-server` (discovery metadata)
   - Local-relay KHÔNG có các endpoints này vì không cần JWT exchange.

3. **Bearer middleware trên `/mcp`** (remote ONLY)
   - Remote-relay: JWT Bearer validation trước khi route tới MCP handler, resolve `sub` → load per-user creds.
   - Local-relay: KHÔNG middleware, creds lấy từ `config.enc` (process-global).

Mọi khác biệt khác = VIOLATION.

## 3. Forbidden Patterns (ANTI-PATTERNS)

- **Dual code path cho same provider set**: Remote dùng `delegatedOAuth {flow: device_code}`, local dùng `relaySchema` paste form → user thấy 2 UI hoàn toàn khác.
- **Provider subset**: Remote ép 1 provider (vd Outlook-only device code) khi local có N providers (Gmail+Yahoo+iCloud+Outlook paste form). Remote PHẢI support đúng N providers.
- **Duplicate form renderer với drift**: 2 copies của `renderXxxCredentialForm` giữa 2 modes, một bên có helpText / validation extra, bên kia không → bug parity.
- **Different validators**: Local regex validate email khác remote regex → reject input khác nhau cho cùng credential.
- **Different error messages**: Local trả "Invalid password", remote trả "Auth failed" → UX phân mảnh.
- **Different success landing**: Local redirect `/success`, remote redirect `/authorized?token=...` với UI khác.

## 4. Code Layout Reference (CORRECT PATTERN)

```typescript
// shared — 1 function duy nhất
function renderEmailCredentialForm(ctx: FormContext): string { ... }

// shared — 1 validator module
import { validateEmailCredentials } from "./validators/email.js";

// entrypoint: transports/http.ts
const server = runLocalServer({
  relaySchema: emailRelaySchema,          // SAME schema cả 2 modes
  renderForm: renderEmailCredentialForm,  // SAME renderer
  validate: validateEmailCredentials,     // SAME validator
  onCredentialsSaved: mode === "local-relay"
    ? async (creds) => writeConfig("better-email-mcp", creds)
    : async (creds, { sub }) => {
        await perUserTokenStore.save(sub, creds);
        return issueJWT(sub);
      },
});
```

Mode-specific difference CHỈ trong `onCredentialsSaved`. Mọi thứ khác shared.

## 5. Credential State Machine

Dùng `CredentialState` enum từ mcp-core (parity cả Python core-py + TypeScript core-ts). KHÔNG reinvent per-server.

```
UNCONFIGURED  → server start, no creds yet
     ↓
AWAITING_USER → relay URL printed, form mounted, waiting for paste/OAuth
     ↓
VALIDATING    → creds received, running validator (test API call / IMAP connect / OTP verify)
     ↓
CONFIGURED    → creds stored (config.enc or perUserTokenStore), MCP protocol ready
```

**Multi-step flows** (OTP, 2FA, device code, phone verification) PHẢI dùng mcp-core primitives:
- `mcp_core.credential.state_machine` (Python) / `@n24q02m/mcp-core/credential` (TS)
- `CredentialState` extensions: `AWAITING_OTP`, `AWAITING_2FA`, `AWAITING_DEVICE_CODE`
- State transitions: `resolve_credential_state()` handles retry/timeout/expiry uniformly.

KHÔNG viết state machine riêng trong từng server. Nếu mcp-core thiếu state → contribute upstream trước, parity cả 2 ngôn ngữ, release mcp-core version, rồi mới dùng.

## 6. Audit Checklist (Verify Parity)

Trước khi merge PR hay release, audit cả 2 modes:

1. **Mount local-relay** — set `MCP_MODE=local-relay`, start server, mở relay URL local (127.0.0.1:port/authorize).
   - Screenshot form.
   - Snapshot HTML: `curl -s http://127.0.0.1:<port>/authorize > local.html`.

2. **Mount remote-relay** — set `MCP_MODE=remote-relay`, start server behind CF Tunnel (hoặc local test với `MCP_RELAY_URL=https://<server>.n24q02m.com`).
   - Screenshot form ở `https://<server>.n24q02m.com/authorize`.
   - Snapshot HTML: `curl -s https://<server>.n24q02m.com/authorize > remote.html`.

3. **Diff**:
   - Visual diff screenshots → pixel-identical except storage indicator nếu có (vd badge "multi-user").
   - `diff local.html remote.html` → chỉ khác OAuth endpoints metadata, không khác form markup.

4. **Source grep**:
   - `grep -rn 'renderEmailCredentialForm' src/` → EXACTLY 1 definition, N callsites.
   - `grep -rn 'validateEmail' src/` → EXACTLY 1 validator module.
   - `grep -rn 'PROVIDERS = ' src/` → EXACTLY 1 constant array, shared cả 2 modes.
   - `grep -rn 'delegatedOAuth\|relaySchema' src/transports/` → KHÔNG được thấy cả 2 cho same provider set.

5. **Behavioral**: paste same creds vào cả 2 URLs → cả 2 phải validate + land success identical (chỉ khác: local ghi `config.enc`, remote trả JWT).

## 7. Case Study: better-email-mcp (2026-04-19, session 80d829f6)

**Bug**: `src/transports/http.ts` rẽ nhánh 2 code paths:
- `remote-relay` → `runLocalServer` với `delegatedOAuth {flow: device_code, upstream: Outlook}` → UI chỉ hiện Microsoft device code `S53THKJLC` + verify URL, Outlook-only.
- `local-relay` → `runLocalServer` với `relaySchema + renderEmailCredentialForm` → paste form multi-provider Gmail/Yahoo/iCloud/Outlook với `email:app-password` input.

User mở `https://better-email-mcp.n24q02m.com/authorize` thấy Outlook-only, scold: "sao lại chỉ có outlook, multi-acc đâu, thiết kế cũ đâu?"

**Fix**: consolidate cả 2 modes về cùng `runLocalServer` call với `relaySchema + renderEmailCredentialForm` shared. Outlook device code vẫn available nhưng như **option in-band** của credential form (click button inline triggers device code flow), KHÔNG phải code path riêng. `onCredentialsSaved` là mode-specific difference duy nhất: local → `writeConfig("better-email-mcp", creds)`, remote → `perUserStore.save(sub, creds)` + `issueJWT(sub)`.

**Lesson**: khi audit relay flow, LUÔN mount cả 2 modes + diff form HTML, đừng trust "cùng codebase chắc giống nhau".
