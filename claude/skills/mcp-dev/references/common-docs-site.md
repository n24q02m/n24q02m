# Common docs site for MCP stack

Single canonical reference for the `mcp.n24q02m.com` common docs site covering 8 MCP servers + mcp-core. Site source lives in `n24q02m/claude-plugins`. All 9 server-side READMEs MUST link here; per-repo `docs/setup-*.md` files MUST be deleted post-migration.

## Domain + ownership

- **Site**: `https://mcp.n24q02m.com` — Cloudflare Pages, Astro Starlight (same stack as `skret.n24q02m.com`)
- **Source repo**: `n24q02m/claude-plugins`, Astro project root at `docs/`
- **Build pipeline**: claude-plugins CD on push-to-main touching `docs/**` OR `plugins/*/{setup,setup-with-agent,tools,modes}.md` → `cd docs && bun install && bun run build` → `wrangler pages deploy docs/dist --project-name=mcp-n24q02m`
- **Custom domain**: `mcp.n24q02m.com` claimed via Cloudflare DNS in CF Pages config

## Sitemap (canonical structure, must not deviate)

```
mcp.n24q02m.com
├── /                                Landing — what is MCP, why these servers, marketplace install
├── /get-started/
│   ├── install-claude-code          Claude Code CLI prerequisite
│   ├── plugin-marketplace           Add n24q02m marketplace
│   ├── modes-overview               stdio / local-relay / remote-relay / remote-oauth
│   ├── multi-user                   Per-JWT-sub credential model
│   └── troubleshooting              Daemon, stale lock, browser open
├── /servers/
│   ├── mcp-core/                    Foundation lib (NOT a server — see "mcp-core framing" below)
│   │   ├── architecture
│   │   ├── trust-model              ← migrate from mcp-core/docs/TRUST-MODEL.md
│   │   ├── migration                ← migrate from mcp-core/docs/migration-*.md
│   │   └── shared-services          ← migrate from mcp-core/docs/shared-services/
│   ├── wet-mcp/
│   │   ├── overview
│   │   ├── setup                    ← migrate from wet-mcp/docs/setup-manual.md
│   │   ├── setup-with-agent         ← migrate from wet-mcp/docs/setup-with-agent.md (also raw .md exposed via GitHub)
│   │   ├── tools
│   │   ├── modes
│   │   └── troubleshooting
│   ├── mnemo-mcp/                   (same skeleton as wet-mcp)
│   ├── better-code-review-graph/
│   ├── imagine-mcp/                 + models page (← migrate from imagine-mcp/docs/models.md)
│   ├── better-telegram-mcp/
│   ├── better-notion-mcp/
│   ├── better-email-mcp/
│   └── better-godot-mcp/
└── /reference/
    ├── mode-matrix                  ← public-safe extract from mcp-dev/references/mode-matrix.md
    ├── tool-layout-standard         N+2 pattern explanation
    ├── relay-flow                   Browser config flow diagram
    ├── multi-user-pattern           PUBLIC_URL + per-sub storage recipe
    └── server-comparison            14-row matrix: server × tools count × auth × multi-user × Docker
```

## Source layout in claude-plugins repo

```
claude-plugins/
├── docs/                            Astro Starlight project root (NEW)
│   ├── astro.config.mjs             Custom content collection loader pulling from ../plugins/*/
│   ├── package.json                 Astro + Starlight deps
│   ├── src/
│   │   ├── content/docs/            Auto-discovered Starlight content (Get Started + Reference pages live here)
│   │   └── content.config.ts        Content collections config (server pages reference plugins/*/ paths)
│   └── public/                      logo, favicon, demo.gif, og-image
└── plugins/<server-name>/           Per-plugin folder (existing in repo)
    ├── .claude-plugin/plugin.json   Existing plugin manifest
    ├── marketplace.json             Existing marketplace metadata
    ├── setup.md                     ← migrate from <server>/docs/setup-manual.md
    ├── setup-with-agent.md          ← migrate from <server>/docs/setup-with-agent.md
    ├── tools.md                     Tool reference (NEW)
    └── modes.md                     Mode flows (NEW)
```

Astro Starlight loader: `astro.config.mjs` declares custom content collection that pulls from `claude-plugins/plugins/*/`. Files at `plugins/<name>/setup.md` render at `mcp.n24q02m.com/servers/<name>/setup/`. Same source files raw-fetched via `https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/<name>/setup-with-agent.md`.

## Agent-feed delivery (mandatory in every server README)

Every MCP server README MUST include this snippet in its "Install" section:

```markdown
## Install with AI agent

Paste this prompt to your AI coding agent (Claude Code, Codex, Gemini CLI, Cursor, Windsurf):

> Install MCP server `<name>` following the steps at
> https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/<name>/setup-with-agent.md
```

URL stability: `<repo>/<branch>/<path>` — only breaks if file path changes. Branch pinned to `main`. Avoid putting raw URLs anywhere except this snippet.

## Per-repo cleanup post-migration

After Spec F lands the docs site:

- **8 MCP server repos**: DELETE `docs/setup-manual.md`, `docs/setup-with-agent.md`. KEEP repo-local content (e.g., `wet-mcp/docs/superpowers/` stays untouched).
- **imagine-mcp**: ADDITIONAL delete `docs/models.md`.
- **mcp-core**: DELETE `docs/TRUST-MODEL.md`, `docs/migration-*.md`, `docs/shared-services/`. Replace `docs/` with single `docs/README.md` redirect: "Documentation moved to https://mcp.n24q02m.com/servers/mcp-core/".
- **All 9 affected READMEs**: update "Documentation" section to link `mcp.n24q02m.com/servers/<name>/`.

## mcp-core framing (NOT a server, special)

mcp-core is a foundation library, not a runnable MCP server. Treat differently:

- Sitemap location: still under `/servers/mcp-core/` for URL consistency with 8 servers, BUT page hero copy says "Foundation library" not "MCP server".
- Sidebar entry: rendered with `[Foundation]` prefix tag in Starlight nav.
- mcp-core does NOT have `setup.md` / `setup-with-agent.md` (no end-user install flow — it's a library used by servers). Instead has: `architecture`, `trust-model`, `migration`, `shared-services`.

## Search

**Pagefind** (Starlight built-in, full-text, free, no external service). NOT Algolia DocSearch (commercial tier required for private/non-OSS contexts).

## Anti-patterns

- After migration, server repo adds new content under its `docs/` folder for setup/tools/modes → drift. Rule: server repo `docs/` may only contain repo-local content (superpowers/, internal architecture notes); user-facing docs live in `claude-plugins/plugins/<name>/`.
- Hardcoded `https://raw.githubusercontent.com/...` references outside README install snippet → fragile cross-repo refs. Rule: only allowed in README "Install with AI agent" section.
- Build per-server site (`wet-mcp.n24q02m.com`, etc.) parallel to common site → contradicts unified-site decision; rule: only `mcp.n24q02m.com` for the 9 repos.
- Treat mcp-core identically to servers (same template, same `setup.md`) → mcp-core has no end-user install; rule: mcp-core MUST have Foundation framing per "mcp-core framing" section.
- agent-feed file > 5KB → exceeds typical LLM context budget for single-prompt install. Rule: split into multiple raw URLs if guide exceeds threshold.

## Memory cross-references

- `feedback_common_docs_site_mcp.md` — incident log + why
- `setup-docs-per-plugin.md` — superseded path correction; this file authoritative for post-migration source layout
