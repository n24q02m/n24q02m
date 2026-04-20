# MCP Category Config Parity

Rules cho parity của `config.py`, `relay_schema.py`, `credential_state.py`, `sync.py` (hoặc TS equivalent) giữa các MCP server cùng category.

Áp dụng khi edit/audit/review code thuộc bất kỳ server nào trong 12-repo scope. Không áp dụng cho relay flow UI (xem `relay-flow.md`) hoặc mode definition (xem `mode-matrix.md`).

## Category Definitions

MCP servers được phân 4 category theo mode matrix. Servers trong cùng category PHẢI parity:

| Category | Servers | Parity scope |
|---|---|---|
| **http local relay** | `wet-mcp`, `mnemo-mcp`, `better-code-review-graph` | `config.py` defaults (bao gồm GDrive Desktop OAuth hardcoded), `relay_schema.py` fields (4 cloud API keys), `credential_state.py` (GDrive device code trigger), `sync.py` (GDrive client) |
| **http remote relay** | `better-telegram-mcp`, `better-email-mcp` | `config.py` defaults, `relay_schema.py` (provider creds + multi-provider paste form), OAuth delegation pattern, per-`sub` storage |
| **http remote oauth** | `better-notion-mcp` | OAuth 2.1 AS pattern, single-provider delegation (parity tự thân — chỉ 1 server trong category) |
| **http local non-relay** | `better-godot-mcp` | Không có credentials; parity = server.py entry point only |

Category xác định qua mode matrix trong `mode-matrix.md`. Server mới phải join 1 trong 4 category hoặc justify category mới trước khi merge.

## Parity Requirement

Servers cùng category PHẢI có **identical structure** cho tất cả file sau:

- **`config.py`** (Python) hoặc **`config.ts`** (TS): field names, defaults, env var aliases, validation rules, pydantic/zod schema shape.
- **`relay_schema.py`** / **`relaySchema.ts`**: field list được render trong relay form, field types, optional/required flags, help text keys.
- **`credential_state.py`**: state machine enum values, transition rules, device-code trigger points.
- **`sync.py`** (nếu server có sync): HTTP client setup, endpoint paths, auth header pattern.

Khác biệt hợp lệ DUY NHẤT:
- Field/tool names riêng của domain (ví dụ `telegram_api_id` vs `email_smtp_host`).
- Storage scope implementation detail (local = `config.enc` single-tenant, remote = `perUserStore.save(sub, creds)` multi-tenant) — nhưng interface contract phải giống.

Mọi khác biệt khác = divergence, REJECT hoặc require user-approved justification ghi trong PR description.

## Pre-Edit Checklist

Trước khi edit bất kỳ file trên của 1 server:

1. **Identify category**: match server với bảng ở Category Definitions.
2. **Open sibling file**: read file tương ứng của ÍT NHẤT 1 sibling server cùng category. Lý tưởng đọc tất cả siblings.
3. **Diff field-by-field**:
   - Defaults trùng không? (ví dụ `google_drive_client_id` hardcoded hay empty?)
   - Env var alias giống pattern không? (ví dụ `WET_GOOGLE_DRIVE_CLIENT_ID` vs `MNEMO_GOOGLE_DRIVE_CLIENT_ID` — prefix khác OK, suffix phải trùng)
   - Field list trong relay schema khớp không?
   - Validation rules (min/max length, regex) khớp không?
4. **Document legitimate difference**: nếu khác biệt là intentional, ghi lý do trong PR body + memory entry. KHÔNG silent commit.

## Add-Field Protocol

Thêm field mới vào config/schema:

1. Xác định category scope của field: local-relay only? remote-relay only? cross-category?
2. Edit **TẤT CẢ** sibling server trong scope trong **same commit** hoặc **same PR batch** (multi-repo PR nếu repo riêng).
3. Ship đồng thời, không stage. KHÔNG "add wet trước, mnemo sau" — drift sẽ xảy ra.
4. Test parity: E2E test của ít nhất 2 siblings phải cùng pass với field mới, không chỉ server origin.
5. Anti-pattern cấm:
   - "Add to wet, mnemo sau" → quên, permanent drift.
   - "Mnemo conservative, không cần field này" → nếu category parity yêu cầu thì conservative = bug.

## Bug-Fix Protocol

Fix bug trong config/schema code:

1. Xác định bug có thuộc shared logic hay server-specific không.
2. Nếu shared (validation, OAuth trigger, state transition): apply parallel sang tất cả siblings cùng category.
3. Single fix commit per server, batch trong cùng session.
4. Run **category parity check** (xem section dưới) sau khi fix, trước khi commit.
5. Verify E2E trên ≥2 siblings.

## Category Parity Check

Command để compare config files across siblings. Chạy trước khi commit bất kỳ edit nào:

```bash
# local-relay: diff config.py across wet/mnemo/crg
diff <(cd ~/projects/wet-mcp && cat src/wet_mcp/config.py) \
     <(cd ~/projects/mnemo-mcp && cat src/mnemo_mcp/config.py)

diff <(cd ~/projects/mnemo-mcp && cat src/mnemo_mcp/config.py) \
     <(cd ~/projects/better-code-review-graph && cat src/crg/config.py)

# local-relay: diff relay_schema.py
diff <(cd ~/projects/wet-mcp && cat src/wet_mcp/relay_schema.py) \
     <(cd ~/projects/mnemo-mcp && cat src/mnemo_mcp/relay_schema.py)

# remote-relay: diff telegram vs email
diff <(cd ~/projects/better-telegram-mcp && cat src/better_telegram_mcp/config.py) \
     <(cd ~/projects/better-email-mcp && cat src/better_email_mcp/config.py)
```

Diff output nên CHỈ chứa domain-specific field names (telegram vs email, wet vs mnemo). Nếu có khác biệt ở default values, env alias pattern, validation, hoặc schema shape → divergence → fix trước commit.

## Case Studies

**2026-04-19 — wet vs mnemo GDrive OAuth defaults (session 80d829f6)**:
- wet-mcp `config.py`: hardcode `google_drive_client_id` + `google_drive_client_secret` (Desktop OAuth Google public secret).
- mnemo-mcp `config.py`: default `""` + `""` → user relay submit → skip GDrive → state=configured nhưng sync chưa setup.
- User scold: "phải đảm bảo thiết kế cấu hình của wet và mnemo giống nhau chứ, có lúc nào tôi bảo làm khác hả".
- Fix: mnemo adopt wet defaults (hardcoded Desktop OAuth per Google public client docs). Memory `feedback_google_oauth_desktop_public.md` corrected.

**2026-04-19 — email local-relay vs remote-relay provider form drift**:
- better-email-mcp `local-relay` mode: `relay_schema.py` render paste form multi-provider (Gmail + Yahoo + iCloud + Outlook).
- better-email-mcp `remote-relay` mode: `transports/http.ts` ép device-code flow Outlook only.
- User mở remote URL chỉ thấy Outlook, scold "multi-acc đâu, thiết kế cũ đâu?".
- Fix: shared `renderXxxCredentialForm` + shared core validator; local/remote chỉ khác `onCredentialsSaved` callback (local writeConfig, remote perUserStore + JWT issuance). Chi tiết rule xem `relay-flow.md`.

## Trigger Keywords

"config.py defaults", "relay_schema", "giống nhau", "parity", "design choice khác", "category parity", "field mới cho MCP server".
