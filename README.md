# n24q02m

## MCP Servers & Plugins

### Quick Install (Claude Code)

```bash
/plugin marketplace add n24q02m/claude-plugins
```

Then `/plugin install <name>@n24q02m-plugins`. All 7 MCP servers in one marketplace.

### Servers

| Server | Description | Agent Setup | Runtime |
|--------|-------------|-------------|---------|
| [wet-mcp](https://github.com/n24q02m/wet-mcp) | Web search, content extraction, and documentation indexing | [Guide](https://raw.githubusercontent.com/n24q02m/wet-mcp/main/docs/setup-with-agent.md) | `uvx wet-mcp` |
| [mnemo-mcp](https://github.com/n24q02m/mnemo-mcp) | Persistent AI memory with hybrid search and cross-machine sync | [Guide](https://raw.githubusercontent.com/n24q02m/mnemo-mcp/main/docs/setup-with-agent.md) | `uvx mnemo-mcp` |
| [better-notion-mcp](https://github.com/n24q02m/better-notion-mcp) | Markdown-first Notion API with 10 composite tools | [Guide](https://raw.githubusercontent.com/n24q02m/better-notion-mcp/main/docs/setup-with-agent.md) | `npx @n24q02m/better-notion-mcp` |
| [better-email-mcp](https://github.com/n24q02m/better-email-mcp) | Email (IMAP/SMTP) with multi-account and auto-discovery | [Guide](https://raw.githubusercontent.com/n24q02m/better-email-mcp/main/docs/setup-with-agent.md) | `npx @n24q02m/better-email-mcp` |
| [better-godot-mcp](https://github.com/n24q02m/better-godot-mcp) | Godot Engine 4.x with 17 composite tools for scenes, scripts, and shaders | [Guide](https://raw.githubusercontent.com/n24q02m/better-godot-mcp/main/docs/setup-with-agent.md) | `npx @n24q02m/better-godot-mcp` |
| [better-telegram-mcp](https://github.com/n24q02m/better-telegram-mcp) | Telegram dual-mode (Bot API + MTProto) with 6 composite tools | [Guide](https://raw.githubusercontent.com/n24q02m/better-telegram-mcp/main/docs/setup-with-agent.md) | `uvx better-telegram-mcp` |
| [better-code-review-graph](https://github.com/n24q02m/better-code-review-graph) | Knowledge graph for token-efficient code reviews | [Guide](https://raw.githubusercontent.com/n24q02m/better-code-review-graph/main/docs/setup-with-agent.md) | `uvx better-code-review-graph` |
| [imagine-mcp](https://github.com/n24q02m/imagine-mcp) | Image and video understanding + generation (2x2x3 provider architecture) | [Guide](https://raw.githubusercontent.com/n24q02m/imagine-mcp/main/docs/setup-with-agent.md) | `uvx imagine-mcp` |

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

### Design Philosophy

These 8 principles are applied consistently across all 8 MCP servers and the relay infrastructure:

1. **Zero-Knowledge Relay** -- E2E encryption (ECDH P-256 + AES-256-GCM). Relay server never sees plaintext credentials. URL fragment secrets stay client-side per RFC 3986.
2. **Composite Tool Pattern** -- One tool per domain with action dispatch. 5-17 tools per server instead of 50+, saving LLM context tokens.
3. **3-Tier Token Optimization** -- Compact descriptions (always loaded), help docs (on demand), MCP resources (deep reference). ~77% token overhead reduction.
4. **Tool Annotations** -- `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` metadata so the LLM knows tool behavior before calling.
5. **Security Defense-in-Depth** -- SSRF prevention, path traversal containment, XPIA boundary tags, error sanitization, rate limiting.
6. **Multi-User HTTP Mode** -- Stateless DCR (HMAC-SHA256), per-user session isolation, AES-256-GCM credential encryption at rest, OAuth 2.1 + PKCE S256.
7. **Degraded Mode** -- Server always starts, even without credentials. Help and config tools work. Data tools return setup instructions instead of crashing.
8. **Zero-Config Relay Setup** -- Auto-open browser, user enters credentials, server receives config via encrypted relay, saves to local config.enc.

## Libraries

| Package | Description | Install |
|---------|-------------|---------|
| [mcp-core](https://github.com/n24q02m/mcp-core) | Unified MCP Streamable HTTP 2025-11-25 transport, OAuth 2.1 AS, lifecycle, install automation, shared embedding daemon | `npm i @n24q02m/mcp-core` / `pip install n24q02m-mcp-core` |
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Lightweight ONNX inference for Qwen3 embedding and reranking models | `pip install qwen3-embed` |
| [web-core](https://github.com/n24q02m/web-core) | Shared web infrastructure: SSRF-safe HTTP, SearXNG search, multi-strategy scraping, stealth browsers | `pip install git+https://github.com/n24q02m/web-core.git` |

## Tools

| Tool | Description | Install |
|------|-------------|---------|
| [jules-task-archiver](https://github.com/n24q02m/jules-task-archiver) | Chrome Extension to bulk-archive completed Jules tasks | [Download zip](https://github.com/n24q02m/jules-task-archiver/releases/latest) |
| [skret](https://github.com/n24q02m/skret) | Cloud-provider secret manager CLI with Doppler/Infisical-grade DX. Zero lock-in, zero server. | `brew install n24q02m/tap/skret` |

## Products

- **KnowledgePrism** -- Chat with your knowledge. Ingest anything (URL, PDF, EPUB, DOCX, CBZ, audio, video, image, text) into a persistent per-project knowledge graph, then produce any format (translation, brief, podcast, slide deck, mindmap, quiz, export). One chat-first agent plans compound requests as a typed capability DAG; ProjectKG is the auto-maintained spine, not a feature. [klprism.com](https://klprism.com)
- **Aiora** -- A health and environment companion for daily wellness. [getaiora.com](https://getaiora.com)
- **LinguaSense** -- Realtime knowledge transfer from any screen or microphone. Desktop + mobile. (coming)
- **Akasha / GWM** -- Research: one graph-centric model with an LLM SOTA teacher, autonomous continuous learning.
