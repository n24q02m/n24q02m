# Nguyen Quang Minh · @n24q02m

[![CD](https://github.com/n24q02m/n24q02m/actions/workflows/cd.yml/badge.svg)](https://github.com/n24q02m/n24q02m/actions/workflows/cd.yml)
[![License: Apache-2.0](https://img.shields.io/github/license/n24q02m/n24q02m)](LICENSE)

[![Site](https://img.shields.io/badge/site-n24q02m.com-blue)](https://n24q02m.com)
[![Last commit](https://img.shields.io/github/last-commit/n24q02m/n24q02m)](https://github.com/n24q02m/n24q02m/commits/main)

> **I design and ship AI systems, developer tools, and MCP infrastructure.**
> On the research side I work on making AI efficient, auditable, and well-behaved.

## Research

I'm interested in AI that stays **efficient, auditable, and reliable** — keeping cost down while every answer remains checkable, and understanding how models behave at their edges. Representative published work:

- **TACET** (Latin: *it is silent*) — *Cost-Amortised Reasoning via Self-Distilling Neuro-Symbolic Cascades: From Knowledge-Graph QA to Regulatory-Compliance Checking.* A three-tier cascade — a sound Datalog engine, a calibrated ComplEx link predictor, and an LLM teacher — with an online distillation loop that mines teacher answers into auditable Horn rules, amortising LLM cost while every symbolic answer ships a replayable proof tree; the same mechanism carries from knowledge-graph QA to streaming GDPR compliance checking. [code](https://github.com/n24q02m/tacet) · [preprint doi:10.5281/zenodo.20621240](https://doi.org/10.5281/zenodo.20621240).

## MCP Servers & Plugins

### Quick Install (Claude Code)

```bash
/plugin marketplace add n24q02m/claude-plugins
```

Then `/plugin install <name>@n24q02m-plugins`. The marketplace ships 8 plugins: the 7 active MCP servers below plus [skret](https://github.com/n24q02m/skret).

### Active servers (4-surface: in-process CLI, MCP stdio, MCP Streamable HTTP, plugin)

| Server | Description | Agent Setup | Install |
|--------|-------------|-------------|---------|
| [wet](https://github.com/n24q02m/wet) | Web search, content extraction, and documentation indexing | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/wet/setup-with-agent.md) | `pip install n24q02m-wet` · CLI: `wet` · MCP: `uvx --from n24q02m-wet wet mcp` |
| [mnemo](https://github.com/n24q02m/mnemo) | Persistent AI memory with hybrid search and knowledge graph | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/mnemo/setup-with-agent.md) | `pip install n24q02m-mnemo` · CLI: `mnemo` · MCP: `uvx --from n24q02m-mnemo n24q02m-mnemo mcp` |
| [crg](https://github.com/n24q02m/crg) | Knowledge graph for token-efficient code reviews | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/crg/setup-with-agent.md) | `pip install n24q02m-crg` · CLI: `crg` · MCP: `uvx n24q02m-crg` |
| [notion](https://github.com/n24q02m/notion) | Markdown-first Notion for AI agents — pages, databases, blocks & comments | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/notion/setup-with-agent.md) | `npm i -g @n24q02m/notion` · CLI: `notion` · MCP: `npx @n24q02m/notion` |
| [email](https://github.com/n24q02m/email) | Email IMAP/SMTP — multi-account management | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/email/setup-with-agent.md) | `npm i -g @n24q02m/email` · CLI: `email` · MCP: `npx @n24q02m/email` |
| [telegram](https://github.com/n24q02m/telegram) | Telegram dual-mode (Bot API + MTProto) — messages, chats, media | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/telegram/setup-with-agent.md) | `pip install n24q02m-telegram` · CLI: `telegram` · MCP: `uvx n24q02m-telegram` |
| [workspace](https://github.com/n24q02m/workspace) | Google Workspace — Docs, Drive, Calendar, Gmail, Sheets, Tasks | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/workspace/setup-with-agent.md) | `npm i -g @n24q02m/workspace` · CLI: `workspace` · MCP: `npx @n24q02m/workspace` |

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

> **Docs hub:** [docs.n24q02m.com](https://docs.n24q02m.com) — unified documentation for the MCP plugin stack, skret, better-semantic-release, hull, and fastretrieval. All 10 CLI/MCP packages are also available via [n24q02m/homebrew-tap](https://github.com/n24q02m/homebrew-tap) and [n24q02m/scoop-bucket](https://github.com/n24q02m/scoop-bucket).

## Libraries

| Package | Description | Install |
|---------|-------------|---------|
| [hull](https://github.com/n24q02m/hull) | Shared Python/TypeScript monorepo core (`hull_core`, `hull_web`, `@n24q02m/hull`) | `pip install n24q02m-hull` · `npm i @n24q02m/hull` |
| [fastretrieval](https://github.com/n24q02m/fastretrieval) | Multi-model retrieval runtime for dense, sparse, late-interaction, image, ColPali, and reranking workloads on ONNX or GGUF | `pip install fastretrieval` · `brew install n24q02m/tap/fastretrieval` · `scoop install fastretrieval` |

## Tools

| Tool | Description | Install |
|------|-------------|---------|
| [better-semantic-release](https://github.com/n24q02m/better-semantic-release) | Drop-in python-semantic-release fork with release-safety guards and `bsr` / `better-semantic-release` CLI. | `pip install better-semantic-release` · `brew install n24q02m/tap/bsr` · `scoop install bsr` |
| [skret](https://github.com/n24q02m/skret) | Cloud-provider secret manager CLI (`AWS SSM`, Azure Key Vault, GCP Secret Manager, OCI Vault, local YAML) with `skret mcp` and Claude Code plugin | `scoop bucket add n24q02m https://github.com/n24q02m/scoop-bucket && scoop install skret` / `brew install n24q02m/tap/skret` · [Docs](https://docs.n24q02m.com/skret/) |

## Archived (read-only — replaced by CLI-first tools or native APIs)

| Repository | Was | Successor / note |
|------------|-----|------------------|
| [mcp-core](https://github.com/n24q02m/mcp-core) | Shared MCP foundation | Replaced by [hull](https://github.com/n24q02m/hull) |
| [web-core](https://github.com/n24q02m/web-core) | Shared web infrastructure | Inlined / replaced by modules in [wet](https://github.com/n24q02m/wet) |
| [agent-chat-plugin](https://github.com/n24q02m/agent-chat-plugin) | Peer agent file chat plugin | Archived |
| [wet-mcp](https://github.com/n24q02m/wet-mcp) | Web MCP server | Renamed to [wet](https://github.com/n24q02m/wet) (PyPI package is now `n24q02m-wet`) |
| [mnemo-mcp](https://github.com/n24q02m/mnemo-mcp) | Memory MCP server | Renamed to [mnemo](https://github.com/n24q02m/mnemo) (PyPI package is now `n24q02m-mnemo`) |
| [better-code-review-graph](https://github.com/n24q02m/better-code-review-graph) | Code-graph MCP server | Renamed to [crg](https://github.com/n24q02m/crg) (PyPI package is now `n24q02m-crg`) |
| [better-notion-mcp](https://github.com/n24q02m/better-notion-mcp) | Notion MCP server | Renamed to [notion](https://github.com/n24q02m/notion) |
| [better-email-mcp](https://github.com/n24q02m/better-email-mcp) | Email (IMAP/SMTP) MCP server | Renamed to [email](https://github.com/n24q02m/email) |
| [better-telegram-mcp](https://github.com/n24q02m/better-telegram-mcp) | Telegram MCP server | Renamed to [telegram](https://github.com/n24q02m/telegram) |
| [better-workspace-mcp](https://github.com/n24q02m/better-workspace-mcp) | Google Workspace MCP server | Renamed to [workspace](https://github.com/n24q02m/workspace) |
| [better-godot-mcp](https://github.com/n24q02m/better-godot-mcp) | Godot Engine MCP server | Archived |
| [imagine-mcp](https://github.com/n24q02m/imagine-mcp) | Image/video understanding + generation MCP server | Archived |
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Qwen3 embedding/reranking package | Superseded by [fastretrieval](https://github.com/n24q02m/fastretrieval) |
| [better-drive](https://github.com/n24q02m/better-drive) | Two-way Google Drive sync | Archived — use [rclone](https://rclone.org) directly |
| [sillstone](https://github.com/n24q02m/sillstone) | Pure-Rust multimedia, image processing, hashing, and SIMD array suite | Archived, no longer maintained |
| [jules-task-archiver](https://github.com/n24q02m/jules-task-archiver) | Jules async task archiver | Archived, no longer maintained |
