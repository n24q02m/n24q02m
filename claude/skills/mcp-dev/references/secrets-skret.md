# Secrets — skret AWS SSM Layout (MCP Stack)

Canonical reference for where each MCP server reads its dynamic credentials from. Companion to `mode-matrix.md` (which mode uses what cred class) and `multi-user-pattern.md` (per-JWT-sub credential isolation).

## Three Credential Categories

The MCP stack splits credentials by lifecycle:

### A — HARDCODED in source (NOT in skret, user does NOT provide)

Public OAuth client identifiers baked into the binary because the upstream provider's docs explicitly classify them as public (Google Desktop client pattern, Microsoft Public Client, Telegram official `api_id`). See `feedback_google_oauth_desktop_public.md`.

| Key | Server | Source location |
|---|---|---|
| Outlook OAuth `client_id` (`d56f8c71-9f7c-43f4-9934-be29cb6e77b0`) | better-email-mcp | `src/tools/helpers/oauth2.ts:88` |
| Telegram `api_id` (`37984984`) + `api_hash` (`2f5f4c76c4de7c07302380c788390100`) | better-telegram-mcp | `src/better_telegram_mcp/config.py:27-28` |
| GDrive Desktop OAuth `client_id` (`147668446467-...`) + `client_secret` (`GOCSPX-...`) | wet-mcp + mnemo-mcp | both `config.py` |

These are **never** in skret. Rotation = source code release. Leak alerts on these = false positive (Google/Microsoft/Telegram all classify them as public).

### B — DYNAMIC (user provides, stored in skret AWS SSM `ap-southeast-1`)

Per-server namespace `/<server>-mcp/prod` holds the values that change per deployment / user / rotation cycle.

| Skret namespace | Key | Used by | Notes |
|---|---|---|---|
| `/better-notion-mcp/prod` | `NOTION_TOKEN` | local relay paste | RELAY_SCHEMA field name verbatim. Legacy `NOTION_INTEGRATION_TOKEN` mirrors same value for older docs. |
| `/better-notion-mcp/prod` | `NOTION_OAUTH_CLIENT_ID`, `NOTION_OAUTH_CLIENT_SECRET` | remote-oauth (notion-mcp.n24q02m.com) | Server-side credentials for Notion OAuth app. NOT in test matrix (notion-oauth reclassified out, see below). |
| `/better-notion-mcp/prod` | `MCP_DCR_SERVER_SECRET` | DCR + JWT signing | Per-server JWT secret. |
| `/better-email-mcp/prod` | `EMAIL_CREDENTIALS` | local + remote relay | Format: `email1:pass1,email2:pass2`. Driver POSTs as single field. |
| `/better-email-mcp/prod` | `OUTLOOK_EMAIL` | email-outlook (remote-relay) | Username only; password empty (server triggers MS device-code). |
| `/better-email-mcp/prod` | `MCP_DCR_SERVER_SECRET` | remote multi-user | |
| `/better-telegram-mcp/prod` | `TELEGRAM_BOT_TOKEN` | telegram-bot (both modes) | Bot mode = paste token, no OTP. |
| `/better-telegram-mcp/prod` | `TELEGRAM_PHONE` | telegram-user (browser-form) | User mode requires OTP + 2FA in browser; phone seeded via skret. |
| `/better-telegram-mcp/prod` | `MCP_DCR_SERVER_SECRET` | remote multi-user | |
| `/wet-mcp/prod` | `JINA_AI_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `COHERE_API_KEY` (optional) | local + remote relay | Optional keys — at least one provider key sufficient for tools/list pass. |
| `/wet-mcp/prod` | `MCP_DCR_SERVER_SECRET` | remote multi-user | |
| `/mnemo-mcp/prod` | same as wet-mcp | local + remote relay | |
| `/better-code-review-graph/prod` | same LLM keys as wet-mcp | local + remote relay | crg uses tree-sitter parse + cloud embedding providers. |
| `/better-code-review-graph/prod` | `MCP_DCR_SERVER_SECRET` | remote multi-user | |
| `/imagine-mcp/prod` | `GEMINI_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY` (optional) | local + remote relay | At least one provider key sufficient. |
| `/imagine-mcp/prod` | `MCP_DCR_SERVER_SECRET` | remote multi-user | |

`MCP_DCR_SERVER_SECRET` — per-server JWT signing secret. Required when `PUBLIC_URL` is set (multi-user remote mode). `bootstrap_skret.sh` generates a fresh 32-byte hex value per server on first run; rotation = re-run with explicit `--rotate` flag.

### C — AUTO-GENERATED (driver/server creates, NOT in skret)

Per-user state generated at runtime from upstream OAuth flow:

| Resource | Storage | Scope |
|---|---|---|
| Outlook refresh token | `~/.better-email-mcp/tokens/<sub>.json` | per-JWT-sub (remote multi-user) |
| GDrive refresh token | `~/.<server>-mcp/subs/<sub>/tokens/google_drive.json` | per-JWT-sub (wet/mnemo multi-user) |
| Telegram session | `~/.better-telegram-mcp/sessions/<sub>.session` | per-JWT-sub |
| Notion access token | mcp-core JWT issuance per request | per-request |

These NEVER touch skret — user-scoped, rotated by upstream, deletable to force re-consent.

## Driver Read Path

`mcp-core/scripts/e2e/skret_loader.py`:

```python
load_namespace(path: str, region: str = "ap-southeast-1") -> dict[str, str]
load_namespace_required(path, required, optional=None) -> dict[str, str]
```

Driver invokes `load_namespace_required` per config in `matrix.yaml` with `required = skret_keys - skret_optional`. Missing required key → `KeyError` → driver fails the config before docker compose up (no wasted container start).

## Bootstrap

```bash
mcp-core/scripts/e2e/bootstrap_skret.sh
```

Generates `MCP_DCR_SERVER_SECRET` for each of the 7 servers if not already present. Other dynamic creds (NOTION_TOKEN, EMAIL_CREDENTIALS, …) require `skret set` interactively — those values are provider-specific and not auto-generatable.

## Reclassification — notion-oauth (2026-04-27)

`notion-oauth` was removed from the T2 matrix per `feedback_no_out_of_band_test_setup.md`: the Notion OAuth app dashboard accepts only pre-registered redirect URIs and supports neither DCR nor loopback wildcards. Local-Docker E2E with random or pinned ports both force out-of-band dashboard registration per clean-state run, which is anti-pattern.

The Notion OAuth `client_id` / `client_secret` remain in skret because production `https://notion-mcp.n24q02m.com` still uses them — the test reclassification only affects the matrix gate, not the deployed instance.

Verification of `notion-oauth` flow happens post-deploy via manual smoke against the production subdomain, not via local Docker spin-up.

## See Also

- `mode-matrix.md` — which mode uses what cred class
- `multi-user-pattern.md` — per-JWT-sub credential isolation pattern
- `e2e-full-matrix.md` — driver execution + harness-readiness gate
- `feedback_google_oauth_desktop_public.md` — why GOCSPX/api_id are not "leaked secrets"
- `feedback_no_out_of_band_test_setup.md` — why notion-oauth was reclassified
- `feedback_env_taxonomy.md` — secret-env vs runtime-env split (dev/prod namespaces)
