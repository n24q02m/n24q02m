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

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

### Design Philosophy

These 8 principles are applied consistently across all 7 MCP servers and the relay infrastructure:

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
| [mcp-relay-core](https://github.com/n24q02m/mcp-relay-core) | Cross-language relay infrastructure for MCP servers (ECDH crypto, config storage, relay client) | `npm i @n24q02m/mcp-relay-core` / `pip install mcp-relay-core` |
| [qwen3-embed](https://github.com/n24q02m/qwen3-embed) | Lightweight ONNX inference for Qwen3 embedding and reranking models | `pip install qwen3-embed` |

## Tools

| Tool | Description | Install |
|------|-------------|---------|
| [jules-task-archiver](https://github.com/n24q02m/jules-task-archiver) | Chrome Extension to bulk-archive completed Jules tasks | [Download zip](https://github.com/n24q02m/jules-task-archiver/releases/latest) |
| [modalcom-ai-workers](https://github.com/n24q02m/modalcom-ai-workers) | GPU-serverless AI workers on Modal.com (embedding, reranking, OCR, ASR) | -- |

## Long-term Direction

**Current** -- [KnowledgePrism](https://klprism.com): Knowledge intelligence platform with multi-model orchestration, RAG pipeline, and knowledge graph-assisted quality assurance across multilingual content.

**Next** -- [Aiora](https://getaiora.com): Health and environmental intelligence platform with deterministic rules, AQI pattern prediction, and real-time sensor data.

**Vision (2027-2028)** -- Graph World Model (Akasha): A paradigm shift from LLM-first to graph-first AI. The knowledge graph becomes the reasoning engine (symbolic rules + GNN inference), with the LLM reduced to a natural language translator. Four model tiers evolve progressively: Echo (LLM + RAG) -> Aura (enhanced graph reasoning) -> Nexus (hybrid symbolic + LLM) -> Akasha (full GWM, minimal LLM). Target: 10-25x cost reduction with full explainability and editability.
