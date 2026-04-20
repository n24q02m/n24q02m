# MCP Tool Layout — N+2 Standard (canonical)

> **Canonical reference** cho tool layout của mọi MCP server trong scope 12 repo.
> File `~/.claude/skills/fullstack-dev/references/mcp-server.md` section "Standard Tool Set" **DEPRECATED** — content đã migrate về đây. Rule trong `~/.claude/CLAUDE.md` block `MCP TOOL LAYOUT CHUẨN (2026-04-18+)` trỏ đến file này.

Chốt 2026-04-18, re-consolidated 2026-04-20.

---

## 1. N+2 Standard

Mỗi MCP server expose CHÍNH XÁC **N domain tools + `config` tool + `help` tool** (N+2 layout).

| Loại | Số lượng | Mục đích | Annotations |
|------|:--------:|----------|-------------|
| **Domain tools** | N (1-15) | Core functionality. Mega-tool pattern với `action` param dispatch | Tùy action (worst-case) |
| **`config` tool** | 1 (bắt buộc) | Credential/relay setup + runtime config (**MERGED**) | readOnlyHint=False, idempotentHint=True |
| **`help` tool** | 1 (bắt buộc) | Full documentation on demand | readOnlyHint=True, idempotentHint=True |

**Breaking change vs. chuẩn cũ**: **KHÔNG có tool `setup` RIÊNG** từ nay. Setup actions (credential/relay flow) được GỘP vào `config` tool dưới dạng action values.

**Lý do**:
- 7 MCP reference repo đang drift 3 patterns khác nhau (`config+setup+help` / `config+help` / `setup+help`) → gây confusion cho LLM khi route action.
- 1 tool `config` duy nhất cho cả lifecycle (setup → runtime) giữ mental model đơn giản.
- Giảm tool count → giảm token overhead trong tool listing.

**Cấm tạo tool `setup` mới** trong MỌI repo (kể cả server mới như `imagine-mcp`). Setup actions PHẢI nằm trong `config`.

---

## 2. `help(topic?)` Contract

```
help(topic: str | None = None) -> str
```

- **topic valid** = **union** của `{domain_tool_name for each domain tool}` + `"config"` + (optional) `"overview"` / alias cho default.
- **topic invalid** → raise `ValueError` với message liệt kê valid topics.
- **topic omitted** → return overview markdown (list available tools + 1-line description mỗi tool).
- Output: markdown string (load từ file `docs/<topic>.md` trong package, KHÔNG inline trong source code).

**Validate BẮT BUỘC**. Không được silently fall back. Ví dụ:

```python
VALID_TOPICS = {"search", "extract", "media", "config", "overview"}  # N domain names + config + overview

async def help(topic: str = "overview") -> str:
    if topic not in VALID_TOPICS:
        raise ValueError(
            f"Unknown topic {topic!r}. Valid: {' | '.join(sorted(VALID_TOPICS))}"
        )
    return (files("my_mcp.docs") / f"{topic}.md").read_text(encoding="utf-8")
```

---

## 3. `config(action, ...)` Contract

```
config(action: str, key: str | None = None, value: str | None = None, ...) -> str
```

**Setup actions** (credential / relay — bắt buộc với mọi server cần credentials):

| Action | Mục đích |
|--------|----------|
| `open_relay` | Mở browser/print relay URL để user nhập credentials |
| `relay_status` | Trạng thái session relay hiện tại (`waiting` / `submitted` / `configured`) |
| `relay_skip` | Bỏ qua relay, fallback env vars |
| `relay_reset` | Xóa credentials hiện tại, reset về clean state |
| `relay_complete` | Confirm setup hoàn tất, commit credentials vào `config.enc` |
| `warmup` | Pre-load heavy resources (embedding model, DB connection, tokenizer) |

**Runtime actions** (tùy server, dispatch qua `action` param):

| Action | Mục đích |
|--------|----------|
| `status` | Hiển thị config hiện tại (DB, embedding, cache, sync, version) |
| `set` | Thay đổi runtime setting (`key` + `value`, validate whitelist) |
| `get` | Đọc 1 runtime setting theo `key` |
| `cache_clear` | Xóa cache |
| Custom | Per-server (vd `docs_reindex`, `setup_sync`, `reindex_graph`) |

**Validate BẮT BUỘC** action chống typo. Error message PHẢI list valid actions:

```python
VALID_ACTIONS = {
    "open_relay", "relay_status", "relay_skip", "relay_reset", "relay_complete", "warmup",
    "status", "set", "get", "cache_clear",
}
if action not in VALID_ACTIONS:
    raise ValueError(f"Unknown action {action!r}. Valid: {' | '.join(sorted(VALID_ACTIONS))}")
```

---

## 4. Python Template (FastMCP)

```python
import sys
from importlib.resources import files

from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from my_mcp.config import settings

mcp = FastMCP("MyServer", instructions="Domain short description.")

DOMAIN_TOOLS = {"search", "extract", "media"}
VALID_HELP_TOPICS = DOMAIN_TOOLS | {"config", "overview"}
VALID_CONFIG_ACTIONS = {
    "open_relay", "relay_status", "relay_skip", "relay_reset", "relay_complete", "warmup",
    "status", "set", "get", "cache_clear",
}


@mcp.tool(description="Search. Actions: docs|code|web.",
          annotations=ToolAnnotations(title="Search", readOnlyHint=True, idempotentHint=True))
async def search(action: str, query: str) -> str:
    ...


@mcp.tool(description="Extract content from URL. Actions: html|pdf|video.",
          annotations=ToolAnnotations(title="Extract", readOnlyHint=True, idempotentHint=True))
async def extract(action: str, url: str) -> str:
    ...


@mcp.tool(description="Discover + download media. Actions: images|videos|audio.",
          annotations=ToolAnnotations(title="Media", readOnlyHint=False, idempotentHint=False))
async def media(action: str, url: str) -> str:
    ...


@mcp.tool(
    description=(
        "Config + relay setup (MERGED, no separate setup tool). Actions: "
        "open_relay|relay_status|relay_skip|relay_reset|relay_complete|warmup|"
        "status|set|get|cache_clear."
    ),
    annotations=ToolAnnotations(title="Config", readOnlyHint=False, idempotentHint=True),
)
async def config(action: str, key: str | None = None, value: str | None = None) -> str:
    if action not in VALID_CONFIG_ACTIONS:
        raise ValueError(f"Unknown action {action!r}. Valid: {' | '.join(sorted(VALID_CONFIG_ACTIONS))}")
    match action:
        case "open_relay": return await _open_relay()
        case "relay_status": return await _relay_status()
        case "relay_skip": return await _relay_skip()
        case "relay_reset": return await _relay_reset()
        case "relay_complete": return await _relay_complete()
        case "warmup": return await _warmup()
        case "status": return await _status()
        case "set": return await _set(key, value)
        case "get": return await _get(key)
        case "cache_clear": return await _cache_clear()


@mcp.tool(description="Full docs. topic: search|extract|media|config|overview.",
          annotations=ToolAnnotations(title="Help", readOnlyHint=True, idempotentHint=True))
async def help(topic: str = "overview") -> str:
    if topic not in VALID_HELP_TOPICS:
        raise ValueError(f"Unknown topic {topic!r}. Valid: {' | '.join(sorted(VALID_HELP_TOPICS))}")
    return (files("my_mcp.docs") / f"{topic}.md").read_text(encoding="utf-8")


def main() -> None:
    logger.remove()
    logger.add(sys.stderr, level=settings.log_level)
    mcp.run()
```

---

## 5. TypeScript Template (`@modelcontextprotocol/sdk`)

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const DOMAIN_TOOLS = new Set(["pages", "databases", "search"]);
const VALID_HELP_TOPICS = new Set([...DOMAIN_TOOLS, "config", "overview"]);
const VALID_CONFIG_ACTIONS = new Set([
  "open_relay", "relay_status", "relay_skip", "relay_reset", "relay_complete", "warmup",
  "status", "set", "get", "cache_clear",
]);

const TOOLS = [
  { name: "pages", description: "Pages. Actions: create|read|update|delete.",
    annotations: { title: "Pages", readOnlyHint: false, idempotentHint: false },
    inputSchema: { type: "object", properties: { action: { type: "string" } }, required: ["action"] } },
  { name: "databases", description: "Databases. Actions: query|update_schema.",
    annotations: { title: "Databases", readOnlyHint: false, idempotentHint: true },
    inputSchema: { type: "object", properties: { action: { type: "string" } }, required: ["action"] } },
  { name: "search", description: "Search. Actions: full_text|semantic.",
    annotations: { title: "Search", readOnlyHint: true, idempotentHint: true },
    inputSchema: { type: "object", properties: { action: { type: "string" } }, required: ["action"] } },
  { name: "config",
    description: "Config + relay setup (MERGED). Actions: open_relay|relay_status|relay_skip|relay_reset|relay_complete|warmup|status|set|get|cache_clear.",
    annotations: { title: "Config", readOnlyHint: false, idempotentHint: true },
    inputSchema: { type: "object", properties: { action: { type: "string" }, key: { type: "string" }, value: { type: "string" } }, required: ["action"] } },
  { name: "help", description: "Full docs. topic: pages|databases|search|config|overview.",
    annotations: { title: "Help", readOnlyHint: true, idempotentHint: true },
    inputSchema: { type: "object", properties: { topic: { type: "string" } } } },
];

const server = new Server({ name: "my-mcp", version: "1.0.0" });
server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));
server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;
  if (name === "help") {
    const topic = (args?.topic as string) ?? "overview";
    if (!VALID_HELP_TOPICS.has(topic)) throw new Error(`Unknown topic '${topic}'. Valid: ${[...VALID_HELP_TOPICS].sort().join(" | ")}`);
    const docsDir = join(dirname(fileURLToPath(import.meta.url)), "docs");
    return { content: [{ type: "text", text: readFileSync(join(docsDir, `${topic}.md`), "utf-8") }] };
  }
  if (name === "config") {
    const action = args?.action as string;
    if (!VALID_CONFIG_ACTIONS.has(action)) throw new Error(`Unknown action '${action}'. Valid: ${[...VALID_CONFIG_ACTIONS].sort().join(" | ")}`);
    return dispatchConfig(action, args);
  }
  if (DOMAIN_TOOLS.has(name)) return dispatchDomain(name, args);
  throw new Error(`Unknown tool '${name}'`);
});

await server.connect(new StdioServerTransport());
```

---

## 6. Category Assignment — Python vs TypeScript

| Server | Stack | Entry point |
|--------|-------|-------------|
| `wet-mcp` | Python (FastMCP) | `uv run wet-mcp` |
| `mnemo-mcp` | Python (FastMCP) | `uv run mnemo-mcp` |
| `better-code-review-graph` | Python (FastMCP) | `uv run crg` |
| `better-telegram-mcp` | Python (FastMCP) | `uv run better-telegram-mcp` |
| `better-notion-mcp` | TypeScript (`@modelcontextprotocol/sdk`) | `npx @n24q02m/better-notion-mcp` |
| `better-email-mcp` | TypeScript (`@modelcontextprotocol/sdk`) | `npx @n24q02m/better-email-mcp` |
| `better-godot-mcp` | TypeScript (`@modelcontextprotocol/sdk`) | `npx @n24q02m/better-godot-mcp` |
| `mcp-core` | Python + TypeScript (monorepo, packages `core-py` + `core-ts`) | library, không entry point server |

**Parity**: domain tools + `config` + `help` layout phải giống hệt nhau giữa Python và TypeScript servers cùng category theo mode matrix (xem `fullstack-dev/references/mcp-server.md` section "Category Config Parity" — đó vẫn là source cho config-level parity; tool-layout parity là content của file này).

---

## 7. Migration Checklist (server chưa N+2)

Áp dụng cho mọi repo drift pattern `config+setup+help` hoặc `setup+help`:

- [ ] **Remove `setup` tool**: xóa `@mcp.tool()` decorator + function signature trong Python, xóa entry trong `TOOLS` array + `CallToolRequestSchema` handler trong TypeScript.
- [ ] **Merge setup actions vào `config`**: move `open_relay`/`relay_status`/`relay_skip`/`relay_reset`/`relay_complete`/`warmup` cases từ `setup` sang match arm của `config` function.
- [ ] **Update `config` tool description**: liệt kê đủ actions (setup + runtime) trong 1 dòng.
- [ ] **Add `help(topic?)` với topic validation**: update `VALID_HELP_TOPICS` = domain tools + `config` + `overview` (KHÔNG còn `setup`).
- [ ] **Update help docstrings / markdown**: xóa `docs/setup.md` (hoặc merge content vào `docs/config.md`), giữ lại 1 file per domain tool + `config.md` + `overview.md`.
- [ ] **Update tool description action lists**: domain tools không cần đổi, nhưng `config` description phải reflect merged action set.
- [ ] **Validate action in `config`**: add whitelist check + error listing valid options.
- [ ] **Update test suite**: remove `setup` tool tests, move relay action tests vào `config` suite, add invalid-topic/invalid-action negative tests.
- [ ] **Update `help` fixture list** (relay E2E checklist trong `fullstack-dev/references/mcp-server.md` coverage matrix): rows `help | setup` → remove; `help | config` remain.
- [ ] **Bump server version**: `feat:` commit vì tool surface thay đổi (N+2 layout); downstream plugin/manifest cần rebuild.
- [ ] **Update CLAUDE.md của repo**: note N+2 layout + actions trong `config`.

Backport 5 drift repo là session-riêng — KHÔNG touch giữa session khác để tránh conflict.

---

## 8. Reference Drift Notice

`~/.claude/skills/fullstack-dev/references/mcp-server.md` section "Standard Tool Set" (lines ~381-432) đã outdated so với file này. **File tool-layout.md này là canonical** cho N+2 layout + `help`/`config` contracts + templates. Khi update:

1. Edit file này trước.
2. Update CLAUDE.md rule block `MCP TOOL LAYOUT CHUẨN (2026-04-18+)` trỏ đến file này.
3. `fullstack-dev/references/mcp-server.md` chỉ giữ 1-pointer section → file này. KHÔNG duplicate content.

Khi phát hiện divergence: file này thắng.
