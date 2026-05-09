# Test B Matrix-in-Settings — Phase 4 Canonical Fixture

(Locked 2026-05-03 by `feedback_settings_matrix_skip_plugin.md`. Re-incident 2026-05-09 → updated rule + skill 2026-05-09.)

## Why matrix-in-settings (not marketplace install)

Marketplace install path adds friction during Test B and was the surface for repeated failure modes:

- **Stale cache**: `~/.claude/plugins/cache/<marketplace>/<plugin>/<version-OLD>/` survives across CC restarts; new BETA on PyPI doesn't auto-pull until cache cleared.
- **Version drift**: `installed_plugins.json` version field vs cached `installPath` folder name vs cached `plugin.json` args pin can mismatch.
- **Env block reset**: CC sometimes resets cached `plugin.json env` after restart (observed wet/imagine 2026-05-02).
- **/reload-plugins unreliable**: doesn't kill OLD process leftovers (observed 2026-05-03).
- **Multi-step pipeline hides bugs**: marketplace metadata → cache resolve → uvx pull → spawn.

Direct `mcpServers` config bypasses ALL of these. One restart, predictable state, easy to inspect.

## Fixture shape

8 plugin × 3 method = **24 entries** in `~/.claude.json mcpServers` (or `~/.claude/settings.json mcpServers`). One CC restart loads tất cả.

3 methods per plugin:

| # | Method | Settings entry shape | What it verifies |
|---|---|---|---|
| 1 | stdio uvx (Python) / npx (TS) — default install equivalent | `{"command": "uvx", "args": [..., "--from", "<plugin>==<beta>", "<plugin>"], "env": {...}}` | Default install path users actually use; uvx/npx cache transitive pin correctness |
| 2 | HTTP Docker | pre-spin `docker run -d -p <port>:8080 ghcr.io/n24q02m/<plugin>:<beta>`, settings entry `{"type": "http", "url": "http://localhost:<port>/mcp"}` | HTTP transport + multi-user PUBLIC_URL deployment (per-JWT-sub credential storage) |
| 3 | stdio Docker | `{"command": "docker", "args": ["run", "-i", "--rm", "-e", "MCP_TRANSPORT", "-e", "<KEY>", "ghcr.io/n24q02m/<plugin>:<beta>"], "env": {"MCP_TRANSPORT": "stdio", "<KEY>": "..."}}` | Container build correctness via stdio path |

### Naming convention for entry IDs

```
<plugin>          # Method 1 stdio uvx / npx
<plugin>-http     # Method 2 HTTP Docker
<plugin>-docker   # Method 3 stdio Docker
```

Tools available trong Claude Code sau restart sẽ là:

- `mcp__plugin_<plugin>__<tool>` (Method 1)
- `mcp__plugin_<plugin>-http__<tool>` (Method 2)
- `mcp__plugin_<plugin>-docker__<tool>` (Method 3)

## Workflow per session

### Step A: Snapshot existing settings

```bash
cp ~/.claude.json ~/.claude.json.bak-$(date +%Y%m%d-%H%M%S)
```

KHÔNG chỉnh trực tiếp khi chưa snapshot. Restore từ backup nếu Test B cần rollback.

### Step B: Generate matrix

Em (Claude) generate 24 entries dựa trên:
- Latest published `:beta` version per plugin (resolve via `gh release list` hoặc `pip index versions <plugin> --pre`)
- Skret namespace per plugin (per `references/secrets-skret.md`)
- Required + optional cred keys per plugin

Script template:

```python
PLUGINS = [
    ("better-godot-mcp", "npm", "@n24q02m/better-godot-mcp", None, []),
    ("better-notion-mcp", "npm", "@n24q02m/better-notion-mcp", "/better-notion-mcp/prod", ["NOTION_TOKEN"]),
    ("better-email-mcp", "npm", "@n24q02m/better-email-mcp", "/better-email-mcp/prod", ["EMAIL_CREDENTIALS"]),
    ("better-telegram-mcp", "pypi", "better-telegram-mcp", "/better-telegram-mcp/prod", ["TELEGRAM_BOT_TOKEN"]),
    ("imagine-mcp", "pypi", "imagine-mcp", "/imagine-mcp/prod", ["GEMINI_API_KEY", "OPENAI_API_KEY", "XAI_API_KEY"]),
    ("wet-mcp", "pypi", "wet-mcp", "/wet-mcp/prod", [...]),
    ("mnemo-mcp", "pypi", "mnemo-mcp", "/mnemo-mcp/prod", [...]),
    ("better-code-review-graph", "pypi", "better-code-review-graph", "/better-code-review-graph/prod", [...]),
]
# For each plugin, emit 3 entries (stdio uvx/npx, HTTP Docker, stdio Docker).
# Multi-user http always includes PUBLIC_URL + MCP_DCR_SERVER_SECRET + CREDENTIAL_SECRET.
```

### Step C: Em write JSON merge into ~/.claude.json mcpServers

Use Edit tool with JSON-aware diff. Preserve existing entries; add 24 new under unique keys. Show diff trước commit.

### Step D: User restart Claude Code

Anh manually `Ctrl+C` current session + re-launch. Em đợi.

### Step E: Em verify 24 entries connected

Sau restart, Em check deferred tools list — phải xuất hiện `mcp__plugin_<plugin>__<tool>` for tất cả 24 entries. Nếu thiếu nào → that entry failed connect → investigate (skret cred missing, Docker port conflict, version pin invalid, etc).

### Step F: Em do 4-step verify per server (per `real-plugin-verification.md`)

- Step 0 (version match): `ls ~/AppData/Roaming/uv/tools/<plugin>/Lib/site-packages/n24q02m_mcp_core-*` (Python) hoặc `grep mcp-core ~/scoop/persist/nodejs24/cache/_npx/<hash>/package.json` (TS) — verify match latest published.
- Step 1 (secret saved): For each entry, ToolSearch `select:mcp__plugin_<entry>__config`, invoke `config` action `status` (OR `read_config(server)` via embedded function call). Verify creds present.
- Step 2 (domain tool call): For each entry, ToolSearch + invoke ≥1 DOMAIN tool from table (xem `real-plugin-verification.md` §2a). Build evidence table:

  ```
  | Entry | Tool | Input excerpt | Result excerpt | PASS/FAIL |
  |---|---|---|---|---|
  | better-notion-mcp | pages | action='list', database_id='<id>' | "[Page 1, Page 2, ...]" | PASS |
  | better-notion-mcp-http | pages | (same) | (same) | PASS |
  | better-notion-mcp-docker | pages | (same) | (same) | PASS |
  | ... | ... | ... | ... | ... |
  ```

- Step 3 (1 daemon per server): Inspect `~/.config/mcp/locks/<server>-*.lock`. Each `<server>` name should have exactly 1 alive lock. Cleanup stale với socket-connect probe per `real-plugin-verification.md` §3.
- Step 4 (single + multi-user mode): Method 1 (stdio uvx) = single-user (no PUBLIC_URL). Method 2 (HTTP Docker) = multi-user (PUBLIC_URL set). Verify per-JWT-sub credential isolation by issuing 2 different JWT sub UUIDs vs Method 2 entry.

### Step G: Restore settings post-test

```bash
cp ~/.claude.json.bak-<ts> ~/.claude.json
```

(Or keep matrix entries if dev workflow benefits from having them around — anh quyết.)

## What's fundamentally different vs T2 driver matrix (DROPPED)

| Surface | T2 driver (DROPPED) | Matrix-in-settings (canonical) |
|---|---|---|
| Plugin lifecycle | `docker compose up` ephemeral container, em as MCP client | Real Claude Code spawn (uvx/npx/docker), CC harness as MCP client |
| Cred fill | driver POST relay form server-to-server | env injection at spawn-time (skret pre-resolved into entry env block) |
| OAuth flow | em parse next_step, browser-form / device-code / oauth-redirect | Real CC handles OAuth UI; em poll setup-status if needed |
| Tool routing | direct `tools/call` via MCP SDK | Through CC's MCP harness (`mcp__plugin_*` deferred tools) |
| 1-daemon check | not part of T2 | Step 3 explicitly verifies |
| Multi-user check | not part of T2 | Step 4 via Method 2 PUBLIC_URL entry |
| Stale cache verify | not testable | Step 0 inspects uvx/npx cache directly |

T2 verified protocol + relay form mechanically. Test B verifies the actual user-facing path.

## Anti-patterns (CẤM, từ memory)

- **Re-add T2 driver matrix entries** to `mcp-core/scripts/e2e/matrix.yaml`. Dropped 2026-05-03. KHÔNG run, KHÔNG reference.
- **Plugin marketplace install path** for Test B fixture. Use direct `mcpServers` config.
- **Skip Step 2 evidence table**. ToolSearch resolve / `__help` / `__config(action='status')` call alone = sloppy verify; metadata tools pass even when domain tier broken.
- **Mark "PASS" without all 24 entries × all 4 steps verified**. Per-server PASS = 4/4 steps PASS × 3 methods. Plugin PASS = 3/3 methods PASS. Test B PASS = 8/8 plugins PASS.
- **Auto-dispatch STABLE after partial Test B**. STABLE Phase 5 chỉ sau Test B 24/24 PASS + user explicit "stable đi" (per `feedback_no_auto_stable_dispatch.md`).

## Cross-references

- `feedback_drop_t2_for_test_b.md` — T2 dropped rationale
- `feedback_settings_matrix_skip_plugin.md` — matrix-in-settings rationale + 3 methods
- `feedback_real_plugin_test_strict.md` — evidence table requirement
- `feedback_test_b_no_implicit.md` — "Test B 4 yêu cầu" anti-pattern reminder
- `feedback_no_auto_stable_dispatch.md` — STABLE only after explicit "stable đi"
- `references/real-plugin-verification.md` — 4-step verify protocol detail
- `references/secrets-skret.md` — per-plugin skret namespace + key list
- `references/work-order-v3.md` — Phase ordering (Phase 4 = this Test B)
