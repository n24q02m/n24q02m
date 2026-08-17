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

Then `/plugin install <name>@n24q02m-plugins`. All 9 MCP servers plus the agent-chat plugin in one marketplace.

### Servers

| Server | Description | Agent Setup | Runtime |
|--------|-------------|-------------|---------|
| [wet-mcp](https://github.com/n24q02m/wet-mcp) | Web search, content extraction, and documentation indexing | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/wet-mcp/setup-with-agent.md) | `uvx wet-mcp` |
| [mnemo-mcp](https://github.com/n24q02m/mnemo-mcp) | Persistent AI memory with hybrid search and cross-machine sync | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/mnemo-mcp/setup-with-agent.md) | `uvx mnemo-mcp` |
| [better-notion-mcp](https://github.com/n24q02m/better-notion-mcp) | Markdown-first Notion API with 10 composite tools | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-notion-mcp/setup-with-agent.md) | `npx @n24q02m/better-notion-mcp` |
| [better-email-mcp](https://github.com/n24q02m/better-email-mcp) | Email (IMAP/SMTP) with multi-account and auto-discovery | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-email-mcp/setup-with-agent.md) | `npx @n24q02m/better-email-mcp` |
| [better-godot-mcp](https://github.com/n24q02m/better-godot-mcp) | Godot Engine 4.x with 17 composite tools for scenes, scripts, and shaders | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-godot-mcp/setup-with-agent.md) | `npx @n24q02m/better-godot-mcp` |
| [better-telegram-mcp](https://github.com/n24q02m/better-telegram-mcp) | Telegram dual-mode (Bot API + MTProto) with 6 composite tools | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-telegram-mcp/setup-with-agent.md) | `uvx better-telegram-mcp` |
| [better-code-review-graph](https://github.com/n24q02m/better-code-review-graph) | Knowledge graph for token-efficient code reviews | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-code-review-graph/setup-with-agent.md) | `uvx better-code-review-graph` |
| [imagine-mcp](https://github.com/n24q02m/imagine-mcp) | Image and video understanding + generation across Gemini, OpenAI, and Grok | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/imagine-mcp/setup-with-agent.md) | `uvx imagine-mcp` |
| [better-workspace-mcp](https://github.com/n24q02m/better-workspace-mcp) | Google Workspace (Docs, Drive, Calendar, Gmail, Sheets, Slides, Tasks, Chat, People, Forms) with multi-account support | [Guide](https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins/better-workspace-mcp/setup-with-agent.md) | `npx @n24q02m/better-workspace-mcp` |

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
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Legacy Qwen3 embedding and reranking package; new features land in [fastretrieval](https://github.com/n24q02m/fastretrieval) while consumers migrate | `pip install qwen3-embed` |
| [web-core](https://github.com/n24q02m/web-core) | Shared web infrastructure: SSRF-safe HTTP, SearXNG search, multi-strategy scraping, stealth browsers | `pip install n24q02m-web-core` |

## Tools

| Tool | Description | Install |
|------|-------------|---------|
| [jules-task-archiver](https://github.com/n24q02m/jules-task-archiver) | Chrome Extension to bulk-archive completed Jules tasks | [Download zip](https://github.com/n24q02m/jules-task-archiver/releases/latest) |
| [skret](https://github.com/n24q02m/skret) | Cloud-provider secret manager CLI with Doppler/Infisical-grade DX. Zero lock-in, zero server. | `brew install n24q02m/tap/skret` |
| [better-drive](https://github.com/n24q02m/better-drive) | Two-way Google Drive sync with `.driveignore` filters, multi-pair config, and a system-tray daemon. Wraps rclone. | `brew install n24q02m/tap/better-drive` |
| [better-semantic-release](https://github.com/n24q02m/better-semantic-release) | Drop-in python-semantic-release fork with release-safety guards for orphan tags and registry collisions. Same config schema, same CLI, same Action interface. | `pip install better-semantic-release` |

## Products

- **KnowledgePrism** -- Chat with your knowledge. Ingest anything (URL, PDF, EPUB, DOCX, CBZ, audio, video, image, text) into a persistent per-project knowledge graph, then produce any format (translation, brief, podcast, slide deck, mindmap, quiz, export). One chat-first agent plans compound requests as a typed capability DAG; ProjectKG is the auto-maintained spine, not a feature. [klprism.com](https://klprism.com)
- **Aiora** -- A health and environment companion for daily wellness. [getaiora.com](https://getaiora.com)
- **LinguaSense** -- Realtime knowledge transfer from any screen or microphone. Desktop + mobile. (coming)
- **Akasha / GWM** *(exploratory research, not a shipped product)* -- a graph-centric world model with an LLM teacher and continuous learning; early-stage.
