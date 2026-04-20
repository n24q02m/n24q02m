# MCP Dev — Canonical 12-repo scope

Đây là **scope BẤT BIẾN** cho mọi session multi-repo thuộc domain MCP stack (audit, backlog clearing, E2E, release cascade).

- **Ngày chốt**: 2026-04-18 (user nhắc lại 3 lần trong session 4739cb45: *"yêu cầu từ đầu session trước là làm việc với 12 repo"*).
- **Skill**: `mcp-dev` (invoke mỗi khi task chạm vào MCP server stack hoặc multi-repo work order fix + test + release).
- **Quy ước**: Khi user nói *"toàn bộ"*, *"fix mọi thứ"*, *"audit all"*, *"làm đầy đủ"* → default expand scope ra **12 repo** dưới đây, không ít hơn.

## Bảng 12 repo (source of truth)

| # | Repo (n24q02m/*) | Role | Local path | Ngôn ngữ |
|---|---|---|---|---|
| 1 | **mcp-core** | Shared MCP primitives (core-ts + core-py parity) | `~/projects/mcp-core` | TS + Python monorepo |
| 2 | **better-notion-mcp** | MCP server — Notion API (default: http remote oauth) | `~/projects/better-notion-mcp` | TS |
| 3 | **better-email-mcp** | MCP server — Email IMAP/SMTP (default: http remote relay) | `~/projects/better-email-mcp` | TS |
| 4 | **better-telegram-mcp** | MCP server — Telegram (default: http remote relay) | `~/projects/better-telegram-mcp` | Python |
| 5 | **wet-mcp** | MCP server — Web Extended Toolkit (default: http local relay) | `~/projects/wet-mcp` | Python |
| 6 | **mnemo-mcp** | MCP server — Memory / SQLite + sqlite-vec (default: http local relay) | `~/projects/mnemo-mcp` | Python |
| 7 | **better-code-review-graph** | MCP server — Code graph / SQLite (default: http local relay) | `~/projects/better-code-review-graph` | Python |
| 8 | **better-godot-mcp** | MCP server — Godot Engine (default: http local non-relay) | `~/projects/better-godot-mcp` | TS |
| 9 | **qwen3-embed** | Embedding / reranker Python library (dependency cho các MCP Python) | `~/projects/qwen3-embed` | Python |
| 10 | **web-core** | Shared web infra package (dependency của wet-mcp — SearXNG runner, Docker fallback) | `~/projects/web-core` | Python |
| 11 | **claude-plugins** | Marketplace cho better-* MCP servers (`plugin.json` cho Claude Code / Codex / Gemini CLI) | `~/projects/claude-plugins` | JSON + scripts |
| 12 | **n24q02m** | Profile repo — public sync target của `~/.claude/` (CLAUDE.md, agents, skills, commands) | `~/projects/n24q02m` | Markdown |

## Vocabulary — số repo user thường nói

User thường dùng các con số để giới hạn scope. Mapping cố định:

- **"7 MCP repos"** = rows #2–#8 (5 Python + 3 TS, đã gồm godot).
- **"8 repos"** = 7 MCP + mcp-core (#1–#8).
- **"11 repos"** = 8 + qwen3-embed + web-core + claude-plugins (#1–#11).
- **"12 repos"** = 11 + n24q02m profile (#1–#12) — **default khi user nói "toàn bộ" / "đầy đủ"**.

Nếu user muốn scope hẹp hơn → PHẢI explicit ("chỉ 7 MCP", "chỉ mcp-core + 7 MCP"). KHÔNG tự đoán hẹp.

## NOT trong scope (tránh lan)

Các repo sau **KHÔNG** thuộc 12-repo scope dù có thể liên quan tangentially:

- **MCP registry / curated lists**: `awesome-mcp-servers`, `mcp-registry` — curated list công khai, không release.
- **App repos** (product layer, khác stack): `KnowledgePrism` (KP), `Aiora`, `QuikShipping` (QShip), `LinguaSense`, `SoundMint`, `TrustHold`.
- **Infra repos** (ops layer, khác nhịp release): `oci-vm-infra`, `oci-vm-prod`.
- **AI/ML research repos**: `virtual-company` (Paperclip VC), `knowledge-core` (GWM).
- **Tooling projects khác**: `skret` (secret CLI), `imagine-mcp` (khi ship sẽ add vào scope), `jules-task-archiver`, `google-form-filler`, `modalcom-ai-workers`.
- **AI traces private**: `.superpower` — private repo cho spec/plan của public repos.

Nếu chạm đến 1 trong các repo trên → scope đã CHUYỂN sang domain khác (infra-devops, ai-ml, product-growth, v.v.), KHÔNG tính vào audit MCP.

## How to apply

1. **Đầu session multi-repo**: đọc file này + chốt scope 12 repo TRƯỚC KHI chạy lệnh audit nào.
2. **Audit / backlog metric default**: chạy trên đúng 12 repo (không 8, không 11). Lệnh chuẩn xem `audit-commands.md`.
3. **Khi user nói "toàn bộ" / "all" / "tất cả"**: interpret là 12 repo, KHÔNG hỏi lại trừ khi user explicit thu hẹp.
4. **Khi phát hiện repo MỚI thuộc MCP stack** (vd `imagine-mcp` khi ship lần đầu, future MCP servers):
   - Update bảng trên trong file này (thêm row #13).
   - Update memory `scope-12-repos.md` song song.
   - Update vocabulary section nếu số tổng đổi.
5. **Khi user scold "bỏ sót repo X"**: đối chiếu với bảng, nếu X thuộc scope nhưng đã miss → root cause audit command không cover hết, fix command TRƯỚC KHI chạy lại.
