# Nguyen Quang Minh · @n24q02m

> I design and ship AI systems, developer tools, and MCP infrastructure.
> On the research side I work on making AI efficient, auditable, and well-behaved.

## Research

I'm interested in AI that stays **efficient, auditable, and reliable** — keeping cost down while every answer remains checkable, and understanding how models behave at their edges. Representative published work:

- **TACET** (Latin: *it is silent*) — *Cost-Amortised Reasoning via Self-Distilling Neuro-Symbolic Cascades: From Knowledge-Graph QA to Regulatory-Compliance Checking.* A three-tier cascade — a sound Datalog engine, a calibrated ComplEx link predictor, and an LLM teacher — with an online distillation loop that mines teacher answers into auditable Horn rules, amortising LLM cost while every symbolic answer ships a replayable proof tree; the same mechanism carries from knowledge-graph QA to streaming GDPR compliance checking. [code](https://github.com/n24q02m/tacet) · [preprint doi:10.5281/zenodo.20621240](https://doi.org/10.5281/zenodo.20621240).

## Writing

- **[Engineering Lessons](https://n24q02m.github.io/engineering-lessons/)** — notes on the machine-learning systems I have built: the approach taken, how it lines up against industry practice, and what was still worth knowing once everything was running. Six posts so far, each in Vietnamese and English. [source](https://github.com/n24q02m/engineering-lessons)

## MCP Servers & Plugins

### Quick Install (Claude Code)

```bash
/plugin marketplace add n24q02m/claude-plugins
```

Then `/plugin install <name>@n24q02m-plugins`. All 8 MCP servers plus the agent-chat plugin in one marketplace.

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

In beta, not yet on a package registry or in the marketplace: [better-workspace-mcp](https://github.com/n24q02m/better-workspace-mcp) — Google Workspace (Docs, Drive, Calendar, Gmail, Sheets, Slides, Tasks, Chat, People, Forms) with multi-account support.

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

### Plugins

| Plugin | Description | Install |
|--------|-------------|---------|
| [agent-chat-plugin](https://github.com/n24q02m/agent-chat-plugin) | Peer agents coordinate through markdown messages in a shared folder — no orchestrator, and waiting costs no tokens | `/plugin install agent-chat-plugin@n24q02m-plugins` |

### Design Philosophy

Shared principles across the MCP servers, built on the mcp-core foundation. The credential-handling ones (1, 6, 8) apply to every server that talks to an upstream account; better-godot-mcp is the exception -- it runs locally with no credentials, so it skips the relay and auth layers entirely.

1. **Zero-Knowledge Relay** -- E2E encryption (ECDH P-256 + AES-256-GCM). Relay server never sees plaintext credentials. URL fragment secrets stay client-side per RFC 3986.
2. **Composite Tool Pattern** -- One tool per domain with action dispatch: 4-17 tools per server instead of dozens of thin endpoints, saving LLM context tokens.
3. **3-Tier Token Optimization** -- Compact descriptions (always loaded), help docs (on demand), and MCP resources (deep reference) keep the always-on tool schema small.
4. **Tool Annotations** -- `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` metadata so the LLM knows tool behavior before calling.
5. **Security Defense-in-Depth** -- SSRF prevention, path-traversal containment, prompt-injection (XPIA) boundary tags around untrusted content, and error sanitization.
6. **Multi-User HTTP Mode** -- Stateless DCR (HMAC-SHA256), per-user session isolation, AES-256-GCM credential encryption at rest, OAuth 2.1 + PKCE S256.
7. **Degraded Mode** -- Server always starts, even without credentials. Help and config tools work. Data tools return setup instructions instead of crashing.
8. **Zero-Config Relay Setup** -- Auto-open browser, user enters credentials, server receives config via encrypted relay, saves to local config.enc.

## Libraries

| Package | Description | Install |
|---------|-------------|---------|
| [mcp-core](https://github.com/n24q02m/mcp-core) | Streamable HTTP transport, OAuth 2.1, browser-based credential setup, lifecycle, and a shared embedding daemon | `npm i @n24q02m/mcp-core` / `pip install n24q02m-mcp-core` |
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Lightweight ONNX inference for Qwen3 embedding and reranking models | `pip install qwen3-embed` |
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
