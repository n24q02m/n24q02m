# Nguyen Quang Minh · @n24q02m

> I design and ship AI systems, developer tools, and MCP infrastructure.
> On the research side I work on making AI efficient, auditable, and well-behaved.

## Research

I'm interested in AI that stays **efficient, auditable, and reliable** — keeping cost down while every answer remains checkable, and understanding how models behave at their edges. Representative published work:

- **TACET** (Latin: *it is silent*) — *Cost-Amortised Reasoning via Self-Distilling Neuro-Symbolic Cascades: From Knowledge-Graph QA to Regulatory-Compliance Checking.* A three-tier cascade — a sound Datalog engine, a calibrated ComplEx link predictor, and an LLM teacher — with an online distillation loop that mines teacher answers into auditable Horn rules, amortising LLM cost while every symbolic answer ships a replayable proof tree; the same mechanism carries from knowledge-graph QA to streaming GDPR compliance checking. [code](https://github.com/n24q02m/tacet) · [preprint doi:10.5281/zenodo.20621240](https://doi.org/10.5281/zenodo.20621240).

## MCP Servers & Plugins

### Quick Install (Claude Code)

```bash
/plugin marketplace add n24q02m/claude-plugins
```

Then `/plugin install <name>@n24q02m-plugins`. The marketplace ships the 7 active MCP servers below.

### Active servers (CLI-first: each ships a native CLI plus an MCP server)

| Server | Description | Agent Setup | Install |
|--------|-------------|-------------|---------|
| [wet](https://github.com/n24q02m/wet) | Web search, content extraction, and documentation indexing | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/wet-mcp/setup-with-agent.md) | `pip install n24q02m-wet` · CLI: `wet` · MCP: `uvx n24q02m-wet` |
| [mnemo](https://github.com/n24q02m/mnemo) | Persistent AI memory with hybrid search and cross-machine sync | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/mnemo-mcp/setup-with-agent.md) | `pip install n24q02m-mnemo` · CLI: `mnemo` · MCP: `uvx n24q02m-mnemo` |
| [crg](https://github.com/n24q02m/crg) | Knowledge graph for token-efficient code reviews | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-code-review-graph/setup-with-agent.md) | `pip install n24q02m-crg` · CLI: `crg` · MCP: `uvx n24q02m-crg` |
| [notion](https://github.com/n24q02m/notion) | Markdown-first Notion for AI agents — pages, databases, blocks & comments | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/notion/setup-with-agent.md) | `npm i -g @n24q02m/better-notion-mcp` · CLI: `notion` · MCP: `npx @n24q02m/better-notion-mcp` |
| [email](https://github.com/n24q02m/email) | Email IMAP/SMTP — multi-account management | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/email/setup-with-agent.md) | `pip install better-email-mcp` · CLI: `email` · MCP: `uvx better-email-mcp` |
| [telegram](https://github.com/n24q02m/telegram) | Telegram dual-mode (Bot API + MTProto) — messages, chats, media | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/telegram/setup-with-agent.md) | `npm i -g @n24q02m/better-telegram-mcp` · CLI: `telegram` · MCP: `npx @n24q02m/better-telegram-mcp` |
| [workspace](https://github.com/n24q02m/workspace) | Google Workspace — Docs, Drive, Calendar, Gmail, Sheets, Tasks | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/workspace/setup-with-agent.md) | `npm i -g @n24q02m/better-workspace-mcp` · CLI: `workspace` · MCP: `npx @n24q02m/better-workspace-mcp` |

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

> **Docs hub:** [mcp.n24q02m.com](https://mcp.n24q02m.com) — unified documentation for MCP servers, skret and better-semantic-release.

## Libraries

| Package | Description | Install |
|---------|-------------|---------|
| [hull](https://github.com/n24q02m/hull) | Shared monorepo core / framework for the MCP server fleet | `npm i @n24q02m/hull` |
| [fastretrieval](https://github.com/n24q02m/fastretrieval) | Multi-model retrieval runtime for dense, sparse, late-interaction, image, ColPali, and reranking workloads on ONNX or GGUF | `pip install fastretrieval` |
| [sillstone](https://github.com/n24q02m/sillstone) | Pure-Rust multimedia, image processing, hashing, and SIMD array suite | Cargo workspace |

## Tools

| Tool | Description | Install |
|------|-------------|---------|
| [jules-task-archiver](https://github.com/n24q02m/jules-task-archiver) | Chrome Extension to bulk-archive completed Jules tasks | [Download zip](https://github.com/n24q02m/jules-task-archiver/releases/latest) |
| [better-semantic-release](https://github.com/n24q02m/better-semantic-release) | Drop-in python-semantic-release fork with release-safety guards for orphan tags and registry collisions. Same config schema, same CLI, same Action interface. | `pip install better-semantic-release` |
| [skret](https://github.com/n24q02m/skret) | Cloud-provider secret manager CLI — secrets without the server (AWS SSM + local YAML; OCI/Azure/GCP roadmap) | `scoop install skret` / `brew install skret` · [Docs](https://mcp.n24q02m.com/skret/) |

## Archived (read-only — replaced by CLI-first tools or native APIs)

| Repository | Was | Successor / note |
|------------|-----|------------------|
| [mcp-core](https://github.com/n24q02m/mcp-core) | Shared MCP foundation | Replaced by [hull](https://github.com/n24q02m/hull) |
| [web-core](https://github.com/n24q02m/web-core) | Shared web infrastructure | Inlined / replaced by modules in [wet](https://github.com/n24q02m/wet) |
| [agent-chat-plugin](https://github.com/n24q02m/agent-chat-plugin) | Peer agent file chat plugin | Archived |
| [wet-mcp](https://github.com/n24q02m/wet-mcp) | Web MCP server | Renamed to [wet](https://github.com/n24q02m/wet) (PyPI package stays `wet-mcp`) |
| [mnemo-mcp](https://github.com/n24q02m/mnemo-mcp) | Memory MCP server | Renamed to [mnemo](https://github.com/n24q02m/mnemo) (PyPI package stays `mnemo-mcp`) |
| [better-code-review-graph](https://github.com/n24q02m/better-code-review-graph) | Code-graph MCP server | Renamed to [crg](https://github.com/n24q02m/crg) (PyPI package stays `better-code-review-graph`) |
| [better-notion-mcp](https://github.com/n24q02m/better-notion-mcp) | Notion MCP server | Renamed to [notion](https://github.com/n24q02m/notion) |
| [better-email-mcp](https://github.com/n24q02m/better-email-mcp) | Email (IMAP/SMTP) MCP server | Renamed to [email](https://github.com/n24q02m/email) |
| [better-telegram-mcp](https://github.com/n24q02m/better-telegram-mcp) | Telegram MCP server | Renamed to [telegram](https://github.com/n24q02m/telegram) |
| [better-workspace-mcp](https://github.com/n24q02m/better-workspace-mcp) | Google Workspace MCP server | Renamed to [workspace](https://github.com/n24q02m/workspace) |
| [better-godot-mcp](https://github.com/n24q02m/better-godot-mcp) | Godot Engine MCP server | Archived |
| [imagine-mcp](https://github.com/n24q02m/imagine-mcp) | Image/video understanding + generation MCP server | Archived |
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Qwen3 embedding/reranking package | Superseded by [fastretrieval](https://github.com/n24q02m/fastretrieval) |
| [better-drive](https://github.com/n24q02m/better-drive) | Two-way Google Drive sync | Archived — use [rclone](https://rclone.org) directly |

## Products

- **KnowledgePrism** -- Chat with your knowledge. Ingest anything (URL, PDF, EPUB, DOCX, CBZ, audio, video, image, text) into a persistent per-project knowledge graph, then produce any format (translation, brief, podcast, slide deck, mindmap, quiz, export). One chat-first agent plans compound requests as a typed capability DAG; ProjectKG is the auto-maintained spine, not a feature. [klprism.com](https://klprism.com)
- **Aiora** -- A health and environment companion for daily wellness. [getaiora.com](https://getaiora.com)
- **LinguaSense** -- Realtime knowledge transfer from any screen or microphone. Desktop + mobile. (coming)
- **Akasha / GWM** *(exploratory research, not a shipped product)* -- a graph-centric world model with an LLM teacher and continuous learning; early-stage.
