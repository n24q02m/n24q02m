# Multi-User Remote Mode — Pattern Reference

**Created**: 2026-04-26 (Tasks 16-20 of e2e-framework-and-multi-user-migration cascade).

Defines how MCP servers expose multi-user remote mode using the existing mcp-core OAuth 2.1 + DCR + per-authorize-sub plumbing — **without** introducing new mcp-core API. Companion to `mode-matrix.md` (which lists modes) and `relay-flow.md` (which covers credential form UX).

## When to apply

A server enters multi-user remote mode iff `PUBLIC_URL` env is set at startup. Same `run_http()` codepath drives both deployments — local single-user (default, `127.0.0.1`) and remote multi-user (`0.0.0.0:8080` + per-sub credential storage).

Applies to all credentialed servers: notion, email, telegram, wet, mnemo, crg, imagine. Not applicable to godot (no creds).

## What mcp-core already provides (do not re-implement)

Verified 2026-04-26 against `mcp-core/packages/core-py/src/mcp_core/`:

- `auth/local_oauth_app.py:214` — fresh per-authorize-session `sub` UUID at every GET /authorize. Concurrent browser tabs receive distinct subs.
- `auth/local_oauth_app.py:69-72` — `SubjectContext = dict[str, str]`; `CredentialsCallback = Callable[[dict, SubjectContext], dict | None]`. The sub is threaded through to `on_credentials_saved`.
- `auth/delegated_oauth_app.py:605` — JWT issued with `sub=entry["sub"]` (per upstream provider user id).
- `auth/delegated_oauth_app.py:618-646` + `auth/local_oauth_app.py:607-645` — `/register` (RFC 7591 echo-style DCR endpoint).
- `oauth/jwt_issuer.py:99` — `issue_access_token(sub, expires_in_seconds=3600)`. Per-server signing keys at `~/.mcp-relay/jwt-keys/<server>_*.pem`.
- `transport/oauth_middleware.py:89` — Bearer middleware sets `request.state.user = claims` (sub accessible to tool handlers).
- `transport/local_server.py:271-336` — `run_local_server(... host: str | None = None ...)`. Pass `host="0.0.0.0"` for remote.

## Server-side recipe (4 changes)

### 1. Per-sub storage helpers in `credential_state.py`

```python
import json
import os
from pathlib import Path


def _sub_data_dir(sub: str) -> Path:
    base = Path(os.environ.get("<SERVER>_DATA_DIR", str(Path.home() / ".<server>-mcp")))
    d = base / "subs" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_for_sub(sub: str, config: dict[str, str]) -> None:
    (_sub_data_dir(sub) / "config.json").write_text(json.dumps(config))


def read_for_sub(sub: str) -> dict[str, str]:
    p = _sub_data_dir(sub) / "config.json"
    return json.loads(p.read_text()) if p.exists() else {}
```

### 2. Sub-aware `save_credentials`

The `on_credentials_saved` callback receives `(creds, context)`. Use `context["sub"]` when `PUBLIC_URL` is set; fall through to single-user shared `config.enc` otherwise.

```python
def save_credentials(config: dict[str, str], context: dict[str, str] | None = None) -> dict | None:
    if os.environ.get("PUBLIC_URL"):
        sub = context.get("sub") if context else None
        if not sub:
            raise RuntimeError("multi-user mode: SubjectContext sub required")
        store_for_sub(sub, config)
        return None
    # single-user path: existing write_config(SERVER_NAME, config) flow
```

Also: skip cross-server cred sharing (e.g. `_share_cloud_keys_to_peers`) in multi-user mode — would leak across tenants.

### 3. PUBLIC_URL switch + refuse-to-start guard in `run_http()`

```python
public_url = os.environ.get("PUBLIC_URL")
if public_url:
    if not os.environ.get("MCP_DCR_SERVER_SECRET"):
        raise SystemExit(
            "<server> refuses to start: PUBLIC_URL set but "
            "MCP_DCR_SERVER_SECRET missing. Multi-user remote mode "
            "requires the DCR secret as proof of intentional multi-user "
            "deployment (prevents accidental single-user credential leak)."
        )
    host = "0.0.0.0"
    port = int(os.environ.get("MCP_PORT", "8080"))
else:
    host = "127.0.0.1"

await run_local_server(mcp, server_name="<server>", relay_schema=RELAY_SCHEMA,
                       host=host, port=port, on_credentials_saved=save_credentials, ...)
```

### 4. Delete legacy `run_remote_relay()` MCP_RELAY_URL function

If the server has a `run_remote_relay()` (single-user `MCP_RELAY_URL` pattern, deprecated 2026-04-25), remove it entirely. In `main()`, replace the `MCP_MODE=remote-relay` branch with:

```python
elif mode == "remote-relay":
    raise SystemExit(
        "MCP_MODE=remote-relay is deprecated since 2026-04-25 (single-user "
        "MCP_RELAY_URL pattern). For multi-user remote: set PUBLIC_URL + "
        "MCP_DCR_SERVER_SECRET and run with default mode."
    )
```

## Required tests per server

```python
@pytest.mark.integration
def test_two_subs_isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("<SERVER>_DATA_DIR", str(tmp_path))
    from <server>.credential_state import read_for_sub, store_for_sub
    store_for_sub("user_a", {"<KEY>": "key_a"})
    store_for_sub("user_b", {"<KEY>": "key_b"})
    assert read_for_sub("user_a") != read_for_sub("user_b")


@pytest.mark.integration
def test_save_credentials_uses_sub_when_public_url_set(tmp_path, monkeypatch):
    monkeypatch.setenv("<SERVER>_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("PUBLIC_URL", "https://<server>.example.com")
    from <server>.credential_state import read_for_sub, save_credentials
    save_credentials({"<KEY>": "k1"}, {"sub": "user_a"})
    save_credentials({"<KEY>": "k2"}, {"sub": "user_b"})
    assert read_for_sub("user_a")["<KEY>"] == "k1"
    assert read_for_sub("user_b")["<KEY>"] == "k2"
```

## Skret namespace per server

Per-server signing keys (compromise isolation, independent rotation):

```
/<server>-mcp/prod/MCP_DCR_SERVER_SECRET   # 32-byte hex, generated once via bootstrap_skret.sh
/<server>-mcp/prod/<dynamic-creds>         # user-provided (notion token, gmail app pwd, ...)
```

Bootstrap: `make bootstrap-skret` in `mcp-core/` (runs `scripts/e2e/bootstrap_skret.sh`).

## Anti-patterns

- **Re-implementing DCR or JWT issuance** — both already exist in mcp-core. Use them.
- **Adding new `create_*_oauth_app` parameters** like `dcr_server_secret` / `token_dir` — the existing `on_credentials_saved` callback already gives you the sub; the existing `JWTIssuer` already issues per-server keys.
- **Single-user `writeConfig(SERVER_NAME, raw)` in remote mode + `// TODO: upstream v1.5 will add sub`** — silent credential leak across tenants. Either implement per-sub NOW or REFUSE start. See `feedback_remote_relay_multi_user_enforcement.md`.
- **Treating multi-user as a separate test config** — it's a deployment property of remote mode. One isolation fixture at mcp-core level + smoke per server (see `e2e-full-matrix.md` configs #3, #5, #8, #10, #12, #14).
- **Sharing `config.enc` across tenants in multi-user mode** — branch on `PUBLIC_URL` and route to `store_for_sub` instead.

## Reference implementations

Verified 2026-04-26 against the `feat/multi-user-remote-mode` (or `feat/gemini-api-key-rename` for imagine) branches in each repo:

| Server | Branch | Commit | Per-sub paths |
|---|---|---|---|
| wet-mcp | `feat/multi-user-remote-mode` | `4a6413d` | `~/.wet-mcp/subs/<sub>/config.json` |
| mnemo-mcp | `feat/multi-user-remote-mode` | `2b4476a` | `~/.mnemo-mcp/subs/<sub>/config.json` |
| better-code-review-graph | `feat/multi-user-remote-mode` | `89d34ba` | `~/.crg/subs/<sub>/{config.json,graph.db}` |
| imagine-mcp | `feat/gemini-api-key-rename` | `e58c16a` | `~/.imagine-mcp/subs/<sub>/config.json` |

mcp-core fixture verifying the per-authorize sub uniqueness contract: `cb2a14b` on `feat/e2e-framework-driver` at `packages/core-py/tests/integration/test_multi_user_isolation.py`.

Notion / Email / Telegram already had multi-user from prior work; the 4-server migration above brings parity for the remaining credentialed servers.
