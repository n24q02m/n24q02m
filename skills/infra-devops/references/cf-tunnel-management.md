# Cloudflare Tunnel + DNS Management

Canonical recipe for adding/removing public hostnames on token-based CF Tunnel (oci-vm-prod, oci-vm-infra) + the corresponding DNS CNAME records. **wrangler does not have route management** despite having `tunnel` namespace — use direct CF API.

## When to use

- Adding new subdomain backed by VM service (e.g. `<plugin>.n24q02m.com → oci-caddy:80`)
- Removing public hostnames after service decommission
- Auditing existing ingress rules against deployed services

## Prerequisites

1. **CF API token** with the right scopes:
   - `Account → Cloudflare Tunnel → Edit` (manage tunnel ingress)
   - `Zone → DNS → Edit` (zone `n24q02m.com` for plugin subdomains)
   - User mints + keeps personally per `feedback_app_namespace_runtime_only.md` (NOT in app skret namespace; OK in personal vault). Account-wide token also valid per `feedback_cf_global_token.md`.
2. **CF_ACCOUNT_ID** in skret `/oci-vm-prod/prod/CF_ACCOUNT_ID` (or `/oci-vm-infra/prod/...`)
3. **Tunnel UUID** — get via `wrangler tunnel list`. Currently:
   - oci-vm-prod: `77ef4269-e94c-428c-ae81-fcdf0db20928`
   - oci-vm-infra: `7bc1e86a-b550-4640-9088-d9eecff6303c`
4. **Zone n24q02m.com ID** — get via `GET /zones?name=n24q02m.com`

## Naming convention (LOCKED)

CF DNS hostnames use **3-part** structure with **hyphen** for staging:
- prod: `<service>.n24q02m.com`
- staging: `<service>-staging.n24q02m.com`

NOT 4-part dot pattern (`<service>.staging.n24q02m.com`) — wastes a CF zone level + drift from existing convention. Verify against `/oci-vm-prod/prod/<SERVICE>_DOMAIN` and `<SERVICE>_STAGING_DOMAIN` skret entries before minting new hostnames.

## DOMAIN env var location

`<SERVICE>_DOMAIN` + `<SERVICE>_STAGING_DOMAIN` env vars live in `/oci-vm-prod/prod/` skret namespace, NOT in plugin-specific `/<plugin>/prod/` namespaces. The Makefile combines them at `make up`. Per-plugin namespaces hold only runtime creds (API keys, OAuth secrets, `MCP_DCR_SERVER_SECRET`, `CREDENTIAL_SECRET` for multi-user HTTP). Routing/domain config is infra-level.

## Recipe: add public hostname

```python
import os, re, json, pathlib, subprocess, urllib.request, urllib.error

# 1. Read OAuth token from wrangler config (account:read + connectivity:admin)
toml = pathlib.Path.home() / "AppData/Roaming/xdg.config/.wrangler/config/default.toml"
oauth = re.search(r'oauth_token = "([^"]+)"', toml.read_text()).group(1)

# 2. Read CF_ACCOUNT_ID from skret
env = os.environ.copy(); env["MSYS_NO_PATHCONV"] = "1"
r = subprocess.run(["skret","get","-e","prod","/oci-vm-prod/prod/CF_ACCOUNT_ID","--plain"],
                   capture_output=True, text=True, env=env,
                   cwd=os.path.expanduser("~/projects/mcp-core/scripts/e2e"))
acct_id = (r.stderr if r.stderr else r.stdout).strip()

TUNNEL_ID = "77ef4269-e94c-428c-ae81-fcdf0db20928"  # oci-vm-prod

def cf_api(method, path, body=None, token=None):
    """Call CF API. Pass `token` to override OAuth (e.g. user's account-wide DNS-edit token)."""
    auth = token or oauth
    url = f"https://api.cloudflare.com/client/v4{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": f"Bearer {auth}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:500]}

# 3. GET current tunnel config (REQUIRED — must read-modify-write, no PATCH)
cur = cf_api("GET", f"/accounts/{acct_id}/cfd_tunnel/{TUNNEL_ID}/configurations")
ingress = cur['result']['config']['ingress']

# 4. Add new hostname before catchall
NEW_HOSTNAMES = ["wet-mcp.n24q02m.com", "wet-mcp-staging.n24q02m.com"]
existing = {i.get('hostname') for i in ingress}
to_add = [h for h in NEW_HOSTNAMES if h not in existing]

if to_add:
    new_entries = [{"hostname": h, "service": "http://caddy:80"} for h in to_add]
    catchall = ingress.pop()  # last entry is catchall (no `hostname` key)
    ingress.extend(new_entries)
    ingress.append(catchall)

    new_cfg = cur['result']['config']
    new_cfg['ingress'] = ingress
    res = cf_api("PUT", f"/accounts/{acct_id}/cfd_tunnel/{TUNNEL_ID}/configurations",
                 {"config": new_cfg})
    assert res.get('success'), res

# 5. Add DNS CNAME records (uses DNS-edit-scoped token — wrangler OAuth lacks this scope)
DNS_TOKEN = os.environ.get("CF_DNS_TOKEN")  # user's account-wide token, paste at runtime
zone = cf_api("GET", "/zones?name=n24q02m.com", token=DNS_TOKEN)
zone_id = zone['result'][0]['id']

for hostname in to_add:
    payload = {"type": "CNAME", "name": hostname,
               "content": f"{TUNNEL_ID}.cfargotunnel.com",
               "ttl": 1, "proxied": True}
    r = cf_api("POST", f"/zones/{zone_id}/dns_records", payload, token=DNS_TOKEN)
    if not r.get('success'):
        # Code 81057 = "An A, AAAA, or CNAME record with that host already exists" (idempotent skip)
        body = r.get('body', '')
        assert "81057" in body or "already exists" in body, f"{hostname}: {body}"
```

## Recipe: remove public hostname

Mirror of add — read config, filter ingress, PUT back. Then DELETE DNS record by record_id.

```python
# Get DNS record id
records = cf_api("GET", f"/zones/{zone_id}/dns_records?name={hostname}", token=DNS_TOKEN)
for rec in records['result']:
    cf_api("DELETE", f"/zones/{zone_id}/dns_records/{rec['id']}", token=DNS_TOKEN)
```

## Anti-patterns

1. **`wrangler tunnel route dns ...`** — does NOT exist. Wrangler `tunnel` namespace lists only `create/delete/info/list/run/quick-start`. The earlier output `Adding ... -> oci-caddy:80` was just an `echo`, not wrangler doing anything.
2. **`/user/tokens/verify`** — lies for Pages-scoped + Tunnel-scoped tokens. Verify by hitting the actual endpoint instead (per `feedback_cf_token_verify_pitfall.md`).
3. **PATCH instead of read-modify-PUT** — CF tunnel `configurations` endpoint has no PATCH; you must GET full config, modify, PUT back.
4. **Putting CF admin tokens in `/<app>/prod` skret** — admin tokens (DNS edit, account-wide) belong in personal vault per `feedback_app_namespace_runtime_only.md`. App namespaces hold only runtime creds.
5. **Forgetting to remove catchall before insert** — last ingress rule is `(catchall)` with no `hostname`. New entries go BEFORE it; catchall must remain last.
6. **DNS proxied=False** — set `proxied=True` for tunnel CNAMEs so requests reach the tunnel daemon. Otherwise direct DNS resolves to `<tunnel-id>.cfargotunnel.com` which is a CF-internal endpoint.

## Service container naming inside tunnel ingress

CF tunnel runs as Docker container `oci-cloudflared` on the `oci-network`. Targets resolve via Docker DNS using **service short name**, not container_name:

- `http://caddy:80` works (caddy is on `oci-network` with service name `caddy`, container_name `oci-caddy`)
- `http://oci-caddy:80` may NOT work depending on Docker networking version

Use `caddy:80` (or whichever short name appears in existing ingress entries) for consistency. Caddy then reverse-proxies to specific plugin containers using `container_name` (`oci-better-notion-mcp:8080`, `oci-wet-mcp:8080`, etc.).

## Verification

After adding hostname:
1. `nslookup <hostname>` → should resolve to `<tunnel-id>.cfargotunnel.com` (CNAME)
2. `curl https://<hostname>/health` → should hit Caddy → upstream service
3. `curl https://<hostname>` without service mapping in Caddyfile → falls through to Caddy default handler (returns 200 "OCI VM Production - API Only" or 404 depending on default)

## Memory references

- `feedback_cf_global_token.md` — existing account-wide CF API token validity
- `feedback_cf_token_verify_pitfall.md` — `/user/tokens/verify` lies
- `feedback_app_namespace_runtime_only.md` — admin tokens stay in personal vault
- `feedback_skret_not_aws_ssm.md` — use `skret` CLI not raw `aws ssm`
- `feedback_no_open_ports.md` — all VM services via CF Tunnel + Caddy, no direct ports
