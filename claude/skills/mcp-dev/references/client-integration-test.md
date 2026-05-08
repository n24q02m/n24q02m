# Client Integration Test — Phase 6 (Post-Release)

Phase 6 của mcp-dev cascade. Entered **sau khi** Phase 4 (Release dispatch) + Phase 5 (Verify) complete. Exit khi all scope clients × all 7 MCP servers đều load + auth + invoke tool thành công.

**Crucial distinction vs Phase 3 (Test A)**:

| | Phase 3 (Test A) | Phase 6 (Test B) |
|---|---|---|
| Timing | Pre-release | Post-release |
| Server source | Source code (`uv run <server>`, `bun run build && node bin/cli.mjs`) | Published artifact (PyPI via `uvx`, npm via `npx`, deployed URL) |
| Client | Python MCP SDK (`mcp.ClientSession + stdio_client` / `streamablehttp_client`) — em runs | Real clients: Claude Code CLI + VS Code GitHub Copilot — user runs |
| Purpose | Verify protocol + relay flow before publishing broken | Verify publish succeeded + plugin marketplace integration works |
| What can break here | Server code bugs, relay form bugs | Packaging bugs, npm/PyPI metadata issues, plugin.json bugs, Claude Code/Copilot MCP client bugs, OAuth client_id drift |

**Anti-pattern (2026-04-21 violation)**: gộp Phase 3 + Phase 6 vào chung một "client test" step. User corrected: "Test qua mcprotocol đã, rồi mới release stable, thì mới có cái mà test với plugin trên claude code và github copilot chứ?!"

## 1. Prerequisite checks

Phase 6 entered only if:
- [ ] Phase 5 verified — all PSR releases tagged + auto-issues filed downstream
- [ ] `npm view @n24q02m/<server>` returns new version
- [ ] `pip index versions <server>` (or `uvx --refresh`) returns new version
- [ ] For deployed modes (notion/email/telegram remote): CF Tunnel endpoint serves new binary (check version in `/.well-known/oauth-authorization-server` or server log)
- [ ] `claude plugin marketplace update` — new plugin versions visible in claude-plugins

Nếu bất kỳ prerequisite không pass → back to Phase 5 debug, không proceed Phase 6.

## 2. Client matrix

**2 clients × 7 MCP servers = 14 base integration tests** (per server×client). Mỗi test flow qua 3 scenarios per mode where applicable (default / local-relay / stdio for servers có multi-mode).

### Client A: Claude Code CLI

- Plugin source: `claude-plugins` marketplace
- Config loaded from `.claude-plugin/plugin.json` → auto-registered on `/reload-plugins` or new session
- OAuth flow: triggered by 401 on `/mcp` endpoint, opens browser, stores JWT in Claude Code state
- Tool invocation: user asks in chat → Claude decides → invokes MCP tool → returns result
- Status check: `claude mcp list`

### Client B: VS Code GitHub Copilot

- Config: `.vscode/mcp.json` workspace-level OR `settings.json` user-level `github.copilot.chat.mcpServers`
- Plugin not available via marketplace → manual JSON config
- OAuth flow: triggered when Copilot Chat invokes tool on un-auth'd server, browser opens
- Tool invocation: user asks in Copilot Chat panel → Copilot invokes MCP tool
- Status check: VS Code "MCP Servers" view in Copilot Chat sidebar

## 3. Per-server-per-client procedure (uniform 8 steps)

```
[pre]  Verify artifact published (prerequisite check section 1)
       Clean state (see clean-state.md) — yes, even though Phase 3 also cleaned;
       Phase 6 tests FRESH install from artifact, so user-side client cache needs cleanup too:
         Claude Code: remove and re-add plugin (forces fresh plugin.json load)
         VS Code Copilot: delete entry from mcp.json, save, re-add

[1]    Client install/register:
         Claude Code: `claude plugin install @n24q02m/better-<server>` (or marketplace UI)
         Copilot: add entry to mcp.json, restart VS Code

[2]    Client health check:
         Claude Code: `claude mcp list` → server shows "Needs authentication" or "Connected" (no "Failed")
         Copilot: MCP Servers view → shows server name without error icon

[3]    Auth flow (trigger by invoking any tool from client, or manual "/mcp" UI):
         Claude Code: `/mcp` → select server → Authenticate → browser opens
         Copilot: invoke tool in chat → browser opens
       User authorizes in browser (real OAuth provider login, not skipped)

[4]    Auth complete — verify JWT/token stored:
         Claude Code: `claude mcp list` shows "Connected"
         Copilot: MCP Servers view shows green icon

[5]    First tool invocation from client (user-initiated):
         Claude Code: ask user natural question that triggers tool (e.g. "list my notion databases")
         Copilot: same in Copilot Chat panel
       Verify: tool called, server returns valid response, client renders result

[6]    Second tool invocation (different tool or different args):
         Tests that JWT persists, tool routing correct across 2+ calls

[7]    Cross-check server logs (deployed mode only):
         `tail -50` deployed server log → confirm:
         - Correct user's JWT sub visible
         - Tool call entries match what client invoked
         - No 401/403 errors mid-session

[8]    Teardown: no need to uninstall; next server test starts fresh.
```

## 4. Server-specific scenarios

### better-notion-mcp (3 modes: remote-oauth / local-relay / stdio)

| Client × Mode | Install command | Auth trigger |
|---|---|---|
| CC + remote-oauth | plugin marketplace | `/mcp` → Authenticate (notion OAuth) |
| CC + local-relay | `claude mcp add --env MCP_MODE=local-relay ...` | tool call triggers local relay URL |
| CC + stdio | `claude mcp add ... stdio` | tool call triggers local relay URL |
| Copilot + remote-oauth | mcp.json with URL | tool call triggers OAuth |
| Copilot + local-relay | mcp.json with command `npx ... --env MCP_MODE=local-relay` | tool call triggers local relay URL |
| Copilot + stdio | mcp.json with command stdio | tool call triggers local relay URL |

### better-email-mcp / better-telegram-mcp

Same pattern as notion. Default mode = remote-relay (not remote-oauth — email/telegram use relay paste form not provider OAuth at MCP layer).

### wet-mcp / mnemo-mcp / better-code-review-graph

- Default: local-relay (no remote-oauth variant for these 3)
- Test local-relay + stdio + remote-relay (self-host via env var) per mode-matrix.

### better-godot-mcp

- http non-relay + stdio modes only
- No credentials → skip step [3]/[4] auth; verify tools/list + tool call directly

## 5. Pass criteria

Per client × server × mode:
- [ ] Plugin/config loads without error
- [ ] Auth flow completes (if applicable)
- [ ] At least 2 tool invocations succeed
- [ ] No 401/403/500 in server log
- [ ] Tool results render correctly in client UI

**ALL GREEN required** trước khi mark Phase 6 complete. Any fail → back to Phase 1 (fix backlog) + re-cascade (new release needed).

## 6. Evidence collection

For each config, record:
- Client name + version (`claude --version`, VS Code build)
- Server version tested (`@n24q02m/better-<x>` from npm / PyPI)
- Install timestamp
- Browser auth screenshots OR redirect URL
- Tool call inputs + outputs (first 2 calls)
- Server log excerpt (deployed modes only)

Save evidence to `cascade-<date>-phase6-results.md`.

## 7. Anti-patterns

- **"Skip Phase 6, Phase 3 was enough"** → violates Test A vs Test B distinction. Publish could break packaging, plugin.json, OAuth client_id refresh, etc. that Phase 3 cannot catch.
- **"Merge Phase 3 + Phase 6 for efficiency"** → 2026-04-21 violation. Phases test different layers; merging hides packaging bugs.
- **"Skip Copilot, Claude Code enough"** → user expects both clients work. Each client has own MCP implementation with quirks (e.g. CC supports dynamic OAuth client registration, Copilot may not).
- **"Use source code for Phase 6 too"** → defeats purpose. Phase 6 must use published artifact exactly as end users would install.
- **"Reuse Phase 3 clean state assumption"** → Phase 6 requires FRESH install-flow clean state (remove plugin, re-add), not just config.enc reset. Client-side caches differ.

## 8. Cross-references

- `e2e-full-matrix.md` — Phase 3 Test A (pre-release)
- `release-cascade.md` — Phase 4 release dispatch (between Test A and Test B)
- `clean-state.md` — config.enc reset (applies to both phases but Phase 6 also needs client-side plugin remove-reinstall)
- `feedback_work_order_fix_test_release.md` — 4-step work order with 2 distinct tests
- `mode-matrix.md` — mode definitions per server (same reference both phases)
