# MCP Dev — Canonical 13-repo scope

Đây là **scope BẤT BIẾN** cho mọi session multi-repo thuộc domain MCP stack (audit, backlog clearing, E2E, release cascade).

- **Ngày chốt**: 2026-04-18 (user nhắc lại 3 lần trong session 4739cb45: *"yêu cầu từ đầu session trước là làm việc với 12 repo"*).
- **Expanded 2026-04-24**: +imagine-mcp (8th MCP server, shipped stable) → **13 repos**.
- **Skill**: `mcp-dev` (invoke mỗi khi task chạm vào MCP server stack hoặc multi-repo work order fix + test + release).
- **Quy ước**: Khi user nói *"toàn bộ"*, *"fix mọi thứ"*, *"audit all"*, *"làm đầy đủ"* → default expand scope ra **13 repo** dưới đây, không ít hơn.

## Bảng 13 repo (source of truth)

| # | Repo (n24q02m/*) | Role | Local path | Ngôn ngữ |
|---|---|---|---|---|
| 1 | **mcp-core** | Shared MCP primitives (core-ts + core-py parity) | `~/projects/mcp-core` | TS + Python monorepo |
| 2 | **better-notion-mcp** | MCP server — Notion API (default: http remote oauth) | `~/projects/better-notion-mcp` | TS |
| 3 | **better-email-mcp** | MCP server — Email IMAP/SMTP (default: http remote relay) | `~/projects/better-email-mcp` | TS |
| 4 | **better-telegram-mcp** | MCP server — Telegram (default: http remote relay) | `~/projects/better-telegram-mcp` | Python |
| 5 | **wet-mcp** | MCP server — Web Extended Toolkit (default: daemon — http local relay + stdio) | `~/projects/wet-mcp` | Python |
| 6 | **mnemo-mcp** | MCP server — Memory / SQLite + sqlite-vec (default: daemon) | `~/projects/mnemo-mcp` | Python |
| 7 | **better-code-review-graph** | MCP server — Code graph / SQLite (default: daemon) | `~/projects/better-code-review-graph` | Python |
| 8 | **better-godot-mcp** | MCP server — Godot Engine (default: http local non-relay) | `~/projects/better-godot-mcp` | TS |
| 9 | **imagine-mcp** | MCP server — image/video understanding + generation (Gemini/OpenAI/Grok), default: daemon | `~/projects/imagine-mcp` | Python |
| 10 | **qwen3-embed** | Embedding / reranker Python library (dependency cho các MCP Python) | `~/projects/qwen3-embed` | Python |
| 11 | **web-core** | Shared web infra package (dependency của wet-mcp — SearXNG runner, Docker fallback) | `~/projects/web-core` | Python |
| 12 | **claude-plugins** | Marketplace cho better-* MCP servers (`plugin.json` cho Claude Code / Codex / Gemini CLI) | `~/projects/claude-plugins` | JSON + scripts |
| 13 | **n24q02m** | Profile repo — public sync target của `~/.claude/` (CLAUDE.md, agents, skills, commands) | `~/projects/n24q02m` | Markdown |

## Vocabulary — số repo user thường nói

User thường dùng các con số để giới hạn scope. Mapping cố định (updated 2026-04-24):

- **"8 MCP servers"** = rows #2–#9 (6 Python + 2 TS — wet, mnemo, crg, telegram, imagine = Python; notion, email, godot = TS).
- **"7 MCP servers"** (lịch sử, pre-imagine-mcp) = rows #2–#8. User nói "7 MCP" khi đang tham chiếu session cũ — hỏi lại nếu context hiện tại → default map sang 8.
- **"9 repos"** = 8 MCP + mcp-core (#1–#9).
- **"12 repos"** = 9 + qwen3-embed + web-core + claude-plugins (#1–#12).
- **"13 repos"** = 12 + n24q02m profile (#1–#13) — **default khi user nói "toàn bộ" / "đầy đủ"**.

Nếu user muốn scope hẹp hơn → PHẢI explicit ("chỉ 8 MCP", "chỉ mcp-core + 8 MCP"). KHÔNG tự đoán hẹp.

## NOT trong scope (tránh lan)

Các repo sau **KHÔNG** thuộc 13-repo scope dù có thể liên quan tangentially:

- **MCP registry / curated lists**: `awesome-mcp-servers`, `mcp-registry` — curated list công khai, không release.
- **App repos** (product layer, khác stack): `KnowledgePrism` (KP), `Aiora`, `QuikShipping` (QShip), `LinguaSense`, `SoundMint`, `TrustHold`.
- **Infra repos** (ops layer, khác nhịp release): `oci-vm-infra`, `oci-vm-prod`.
- **AI/ML research repos**: `virtual-company` (Paperclip VC), `knowledge-core` (GWM).
- **Tooling projects khác**: `skret` (secret CLI), `jules-task-archiver`, `google-form-filler`, `modalcom-ai-workers`.
- **AI traces private**: `.superpower` — private repo cho spec/plan của public repos.

Nếu chạm đến 1 trong các repo trên → scope đã CHUYỂN sang domain khác (infra-devops, ai-ml, product-growth, v.v.), KHÔNG tính vào audit MCP.

## How to apply

1. **Đầu session multi-repo**: đọc file này + chốt scope 13 repo TRƯỚC KHI chạy lệnh audit nào.
2. **Audit / backlog metric default**: chạy trên đúng 13 repo (không 9, không 12). Lệnh chuẩn xem `audit-commands.md`.
3. **Khi user nói "toàn bộ" / "all" / "tất cả"**: interpret là 13 repo, KHÔNG hỏi lại trừ khi user explicit thu hẹp.
4. **Khi phát hiện repo MỚI thuộc MCP stack** (vd future MCP servers):
   - Update bảng trên trong file này (thêm row #14).
   - Update memory `scope-12-repos.md` song song.
   - Update vocabulary section nếu số tổng đổi.
5. **Khi user scold "bỏ sót repo X"**: đối chiếu với bảng, nếu X thuộc scope nhưng đã miss → root cause audit command không cover hết, fix command TRƯỚC KHI chạy lại.
