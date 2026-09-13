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

Then `/plugin install <name>@n24q02m-plugins`. The marketplace ships every server below plus the agent-chat plugin.

### Active servers (CLI-first: each ships a native CLI plus an MCP server)

| Server | Description | Agent Setup | Install |
|--------|-------------|-------------|---------|
| [wet](https://github.com/n24q02m/wet) | Web search, content extraction, and documentation indexing | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/wet-mcp/setup-with-agent.md) | `pip install wet-mcp` · CLI: `wet` · MCP: `uvx wet-mcp` |
| [mnemo](https://github.com/n24q02m/mnemo) | Persistent AI memory with hybrid search and cross-machine sync | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/mnemo-mcp/setup-with-agent.md) | `pip install mnemo-mcp` · CLI: `mnemo` · MCP: `uvx mnemo-mcp` |
| [crg](https://github.com/n24q02m/crg) | Knowledge graph for token-efficient code reviews | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-code-review-graph/setup-with-agent.md) | `pip install better-code-review-graph` · CLI: `crg` · MCP: `uvx better-code-review-graph` |

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

### Plugins

| Plugin | Description | Install |
|--------|-------------|---------|
| [agent-chat-plugin](https://github.com/n24q02m/agent-chat-plugin) | Peer agents coordinate through markdown messages in a shared folder — no orchestrator, and waiting costs no tokens | `/plugin install agent-chat-plugin@n24q02m-plugins` |

## Libraries

| Package | Description | Install |
|---------|-------------|---------|
| [mcp-core](https://github.com/n24q02m/mcp-core) | Streamable HTTP transport, OAuth 2.1, browser-based credential setup, lifecycle, and a shared embedding daemon | `npm i @n24q02m/mcp-core` / `pip install n24q02m-mcp-core` |
| [fastretrieval](https://github.com/n24q02m/fastretrieval) | Multi-model retrieval runtime for dense, sparse, late-interaction, image, ColPali, and reranking workloads on ONNX or GGUF | `pip install fastretrieval` |
| [web-core](https://github.com/n24q02m/web-core) | Shared web infrastructure: SSRF-safe HTTP, SearXNG search, multi-strategy scraping, stealth browsers | `pip install n24q02m-web-core` |

## Tools

| Tool | Description | Install |
|------|-------------|---------|
| [jules-task-archiver](https://github.com/n24q02m/jules-task-archiver) | Chrome Extension to bulk-archive completed Jules tasks | [Download zip](https://github.com/n24q02m/jules-task-archiver/releases/latest) |
| [better-semantic-release](https://github.com/n24q02m/better-semantic-release) | Drop-in python-semantic-release fork with release-safety guards for orphan tags and registry collisions. Same config schema, same CLI, same Action interface. | `pip install better-semantic-release` |

## Archived (read-only — replaced by CLI-first tools or native APIs)

| Repository | Was | Successor / note |
|------------|-----|------------------|
| [wet-mcp](https://github.com/n24q02m/wet-mcp) | Web MCP server | Renamed to [wet](https://github.com/n24q02m/wet) (PyPI package stays `wet-mcp`) |
| [mnemo-mcp](https://github.com/n24q02m/mnemo-mcp) | Memory MCP server | Renamed to [mnemo](https://github.com/n24q02m/mnemo) (PyPI package stays `mnemo-mcp`) |
| [better-code-review-graph](https://github.com/n24q02m/better-code-review-graph) | Code-graph MCP server | Renamed to [crg](https://github.com/n24q02m/crg) (PyPI package stays `better-code-review-graph`) |
| [better-notion-mcp](https://github.com/n24q02m/better-notion-mcp) | Notion MCP server | Use the official Notion API/SDK directly |
| [better-email-mcp](https://github.com/n24q02m/better-email-mcp) | Email (IMAP/SMTP) MCP server | Use standard IMAP/SMTP tooling |
| [better-telegram-mcp](https://github.com/n24q02m/better-telegram-mcp) | Telegram MCP server | Use the official Telegram Bot API / MTProto clients |
| [better-godot-mcp](https://github.com/n24q02m/better-godot-mcp) | Godot Engine MCP server | Use Godot's native scripting/CLI |
| [better-workspace-mcp](https://github.com/n24q02m/better-workspace-mcp) | Google Workspace MCP server | Use Google Workspace APIs directly |
| [imagine-mcp](https://github.com/n24q02m/imagine-mcp) | Image/video understanding + generation MCP server | Use provider-native APIs (Gemini, OpenAI, Grok) |
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Qwen3 embedding/reranking package | Superseded by [fastretrieval](https://github.com/n24q02m/fastretrieval) (`pip install qwen3-embed` still works) |
| [skret](https://github.com/n24q02m/skret) | Secret-manager CLI | Use AWS SSM Parameter Store directly (store layout unchanged) |
| [better-drive](https://github.com/n24q02m/better-drive) | Two-way Google Drive sync | Use [rclone](https://rclone.org) directly |

## Products

- **KnowledgePrism** -- Chat with your knowledge. Ingest anything (URL, PDF, EPUB, DOCX, CBZ, audio, video, image, text) into a persistent per-project knowledge graph, then produce any format (translation, brief, podcast, slide deck, mindmap, quiz, export). One chat-first agent plans compound requests as a typed capability DAG; ProjectKG is the auto-maintained spine, not a feature. [klprism.com](https://klprism.com)
- **Aiora** -- A health and environment companion for daily wellness. [getaiora.com](https://getaiora.com)
- **LinguaSense** -- Realtime knowledge transfer from any screen or microphone. Desktop + mobile. (coming)
- **Akasha / GWM** *(exploratory research, not a shipped product)* -- a graph-centric world model with an LLM teacher and continuous learning; early-stage.
