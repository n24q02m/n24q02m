# README parity across MCP stack

All public MCP servers are **Tier 1 Flagship** OSS. They must share the same README structure, tone, and assets, diverging only on content.

**Authoritative template**: `~/.claude/skills/infra-devops/references/repo-structure.md` → "Tier 1 — Flagship README" section.
**Reference implementation**: https://github.com/n24q02m/skret/blob/main/README.md

## Scope — Canonical source

Scope is defined by two GitHub Stars lists on `n24q02m`:

- **Productions** (`https://github.com/stars/n24q02m/lists/productions`) — user-facing products
- **Scripts** (`https://github.com/stars/n24q02m/lists/scripts`) — infra, tooling, profile

Fetch with:

```bash
gh api graphql -f query='
query { viewer { lists(first:10) { nodes { name items(first:100) { nodes { ... on Repository { nameWithOwner isPrivate isArchived } } } } } } }'
```

### Productions (18 repos — 2026-04-20 snapshot)

**Tier 1 Flagship public (14):**

MCP servers (8): `wet-mcp`, `better-telegram-mcp`, `better-godot-mcp`, `better-email-mcp`, `better-notion-mcp`, `mnemo-mcp`, `better-code-review-graph`, `imagine-mcp`

Core libraries (3): `mcp-core`, `web-core`, `qwen3-embed`

CLI / marketplace / tool (3): `skret`, `claude-plugins`, `jules-task-archiver`

**Tier 1 internal (4 private):** `QuikShipping`, `KnowledgePrism`, `Aiora`, `knowledge-core` — still structured like Tier 1 but not user-facing externally.

### Scripts (9 repos)

**Tier 2 public (3):** `n24q02m` (profile), `scoop-bucket`, `homebrew-tap`

**Infra private (6):** `oci-vm-infra`, `oci-vm-prod`, `virtual-company`, `google-form-filler`, `.superpower`, `modalcom-ai-workers` — README follows Tier 2 where ops readers benefit; internal tools can skip.

## Required sections per tier

| Section | Tier 1 Flagship | Tier 2 |
|---|---|---|
| Hero logo + title | Yes | Title only |
| Tagline one-liner | Yes | Yes |
| 2-row badges | Yes | Yes |
| Nav links (Docs · Install · Quick · Community) | Yes | — |
| Example code | Yes | — |
| Demo gif (VHS) | Yes | — |
| TOC | Yes | — |
| Why X? | Yes | — |
| Features bullets | Yes | — |
| Install matrix table | Yes | Single install snippet |
| Quick start numbered | Yes | — |
| Comparison table | Yes (vs competitors) | — |
| Documentation links | Yes (docs site) | README-only |
| Command / tool overview | Yes | — |
| Contributing | Link or inline | Link |
| Sponsors | GitHub Sponsors | — |
| Acknowledgments | Yes | — |
| License | Yes | Yes |

## Assets per Tier 1 Flagship repo

```
docs/public/
  logo.svg           # 120px square
  logo-dark.svg      # dark-mode variant
  favicon.svg
  favicon.ico
  apple-touch-icon.png
  banner.png         # 1200×400
  og-image.png       # 1200×630 (GitHub social preview + Twitter Card)
  demo.gif           # VHS recording, 30s happy path
```

Generation pipeline (see skret for reference):
- Branding: `scripts/gen-branding.py` via Gemini Imagen 4 Ultra
- Demo: `.github/workflows/demo.yml` renders `demo.tape` via `charmbracelet/vhs-action@v2`, auto-commits `demo.gif` back to `main`

**Social preview upload** — no REST endpoint exists. Manual step: GitHub repo → Settings → Social preview → upload `og-image.png`. Document this once per repo in a tracking issue.

## MCP-specific additions on top of Tier 1 base

MCP server repos must also include:

1. **Install table** — rows per MCP client (Claude Code, Codex, Gemini CLI, Cursor, Windsurf — whichever is officially supported)
2. **Mode badge** in header — `local-stdio` / `local-relay` / `remote-relay` per `mode-matrix.md`
3. **Config example** in Quick Start
4. **Tool surface** — list of N tools exposed (plus infra tools `help` + `config`) per `tool-layout.md`
5. **Relay screenshot** if the server supports relay mode

## Roll-out flow

When maturing the template on a flagship (skret or mcp-core):

1. Land pattern on one repo, verify it renders on the docs site + GitHub OG previews
2. Update `~/.claude/skills/infra-devops/references/repo-structure.md` Tier 1 section
3. Update this file (`readme-parity.md`) with new delta
4. Open a tracking issue on each downstream repo: `chore: align README with Tier 1 template vN`
5. Batch 3-4 repos per PR (single-repo PRs create churn; too large = review fatigue)
6. Verify consistency: `for r in wet-mcp mnemo-mcp ...; do gh api repos/n24q02m/$r/readme --jq .size; done`

## Anti-patterns

- README with only a title — fail (Tier 2 minimum is title + tagline + 2-row badges)
- Copy-paste skret README verbatim into an MCP server — product framing differs; rewrite content
- Out-of-sync demo gif (README shows old UI) — the VHS workflow prevents this; don't commit gifs manually
- Missing logo / OG assets — breaks social sharing + GitHub card
- Installing a README template before the flagship stabilizes — causes rework when template shifts; wait until flagship v1.0 stable
- Skipping scope check — if scope changes, the two Stars lists are the single source of truth, not guess lists in memory
