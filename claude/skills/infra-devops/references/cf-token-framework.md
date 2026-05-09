# Cloudflare Token 3-Category Framework

(Locked 2026-05-08 by `feedback_cf_global_token.md`. Consolidated 2026-05-09 from CLAUDE.md inline detail.)

## 3 Categories

Phân biệt rõ TRƯỚC khi xử lý op CF — không conflate, không ASK user khi token đã trong skret.

### 1. Project token (per app)

- **Path pattern**: `/<App>/<env>/<APP>_CF_PAGES_API_TOKEN`
- **Scope**: 1 Pages project per app — Aiora / KnowledgePrism / QuikShipping / skret / mcp project
- **Use**: Pages CD only (deploy preview / production)
- **NOT for**: zone edit, DNS, Workers, R2, Tunnel, account-wide ops

### 2. Infra token

- **Path pattern**: `/oci-vm-{infra,prod}/{prd,prod}/CF_R2_*` + `/CF_TUNNEL_TOKEN`
- **Scope**: VM-level R2 + Tunnel only
- **Use**: VM ops (R2 bucket access, Tunnel run)
- **NOT for**: Pages deploy, Zone edit, account-wide audit

### 3. Full-access dev token

- **Path**: `/n24q02m/dev/CF_DEV_TOKEN` (region `ap-southeast-1`)
- **Label** in Cloudflare dashboard: "Edit almost everything resource"
- **Scope**: Pages + Zone + DNS + Workers + R2 cross all n24q02m zones
- **Use**: dashboard-replacement automation — em làm thay user; cross-zone DNS edit; account-wide audit
- **NEVER ask user** to paste this token; retrieve from skret if op requires.

## Retrieval recipe

Skret CLI has a known bug retrieving the dev token entry. AWS SSM direct read is the documented exception for this category (read-only retrieval, NOT for write):

```bash
MSYS_NO_PATHCONV=1 AWS_REGION=ap-southeast-1 \
  aws ssm get-parameter \
  --name /n24q02m/dev/CF_DEV_TOKEN \
  --with-decryption \
  --query 'Parameter.Value' \
  --output text
```

For project + infra tokens, normal `skret env -e prod --path=<ns>` works.

## Verify validity

**Always hit a real endpoint** to verify token, NEVER `/user/tokens/verify`:

```bash
TOKEN=$(<retrieve as above>)
curl -s "https://api.cloudflare.com/client/v4/zones?name=n24q02m.com" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.success'  # expect true
```

`/user/tokens/verify` lies for scoped tokens — returns `success: true` even when token can't actually access the resource. Per `feedback_cf_token_verify_pitfall.md`.

## Anti-patterns

- **Ask user paste CF token** when it's already in skret — vi phạm 2026-05-08 (5 pushback consecutive)
- **Use project token for zone edit** — scope mismatch, will 403
- **Use dev token for Pages CD step in production** — overprivileged for a CD job that only needs project scope
- **Hunt CF token in app skret namespace** when op is admin-level — see `feedback_app_namespace_runtime_only.md`

## Cross-references

- Memory `feedback_cf_global_token.md` (2026-05-08 rewrite, 3-category framework origin)
- Memory `feedback_cf_token_verify_pitfall.md` (`/user/tokens/verify` lies)
- Memory `feedback_app_namespace_runtime_only.md` (admin op shouldn't hunt app namespace)
- Skill `~/.claude/skills/infra-devops/references/cf-tunnel-management.md` (Tunnel-specific ops use infra token)
