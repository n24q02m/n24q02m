# n24q02m

## Quick Install (Claude Code)

```bash
/plugin marketplace add n24q02m/claude-plugins
```

Then `/plugin install <name>@n24q02m-plugins`. All 7 MCP servers in one marketplace.

## MCP Servers & Plugins

| Server | Description | Agent Setup | Runtime |
|--------|-------------|-------------|---------|
| [wet-mcp](https://github.com/n24q02m/wet-mcp) | Web search, content extraction, and documentation indexing | [Guide](https://raw.githubusercontent.com/n24q02m/wet-mcp/main/docs/setup-with-agent.md) | `uvx wet-mcp` |
| [mnemo-mcp](https://github.com/n24q02m/mnemo-mcp) | Persistent AI memory with hybrid search and cross-machine sync | [Guide](https://raw.githubusercontent.com/n24q02m/mnemo-mcp/main/docs/setup-with-agent.md) | `uvx mnemo-mcp` |
| [better-notion-mcp](https://github.com/n24q02m/better-notion-mcp) | Markdown-first Notion API with 9 composite tools | [Guide](https://raw.githubusercontent.com/n24q02m/better-notion-mcp/main/docs/setup-with-agent.md) | `npx @n24q02m/better-notion-mcp` |
| [better-email-mcp](https://github.com/n24q02m/better-email-mcp) | Email (IMAP/SMTP) with multi-account and auto-discovery | [Guide](https://raw.githubusercontent.com/n24q02m/better-email-mcp/main/docs/setup-with-agent.md) | `npx @n24q02m/better-email-mcp` |
| [better-godot-mcp](https://github.com/n24q02m/better-godot-mcp) | Godot Engine 4.x with 17 composite tools for scenes, scripts, and shaders | [Guide](https://raw.githubusercontent.com/n24q02m/better-godot-mcp/main/docs/setup-with-agent.md) | `npx @n24q02m/better-godot-mcp` |
| [better-telegram-mcp](https://github.com/n24q02m/better-telegram-mcp) | Telegram dual-mode (Bot API + MTProto) with 6 composite tools | [Guide](https://raw.githubusercontent.com/n24q02m/better-telegram-mcp/main/docs/setup-with-agent.md) | `uvx better-telegram-mcp` |
| [better-code-review-graph](https://github.com/n24q02m/better-code-review-graph) | Knowledge graph for token-efficient code reviews | [Guide](https://raw.githubusercontent.com/n24q02m/better-code-review-graph/main/docs/setup-with-agent.md) | `uvx better-code-review-graph` |

> **Setup any server:** Copy the Agent Setup guide link and send it to your AI agent with "Please set up this MCP server for me."

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
