# Claude Code Setup Guide

Hướng dẫn thiết lập Claude Code trên máy mới để đồng bộ với cấu hình hiện tại.

## Yêu cầu

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (>= 2.1.x)
- [bun](https://bun.sh/) (chạy MCP servers TypeScript)
- [uv](https://docs.astral.sh/uv/) (chạy MCP servers Python)
- Python 3.13 (pinned cho mọi Python MCP server)
- [mise](https://mise.jdx.dev/) (quản lý runtime versions)

## Bước 1: Clone repo

```bash
git clone https://github.com/n24q02m/n24q02m.git ~/projects/n24q02m
cd ~/projects/n24q02m
```

## Bước 2: Copy global CLAUDE.md

```bash
cp claude-code/CLAUDE.md ~/.claude/CLAUDE.md
```

File này chứa các quy tắc chung áp dụng cho mọi project (ngôn ngữ, chuẩn mực code, security).

## Bước 3: Copy settings.json

```bash
cp claude-code/settings.json ~/.claude/settings.json
```

File này chứa:

- **Plugins**: Danh sách plugins được bật (official + marketplace)
- **Marketplaces**: n24q02m-plugins (n24q02m — 7 MCP servers), cc-marketplace (kenryu42)
- **Env vars**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`
- **Permissions**: `bypassPermissions` mode (bỏ qua xác nhận cho mọi action)
- **Effort**: `high` (reasoning effort mặc định)

Sau khi copy, cần đăng ký marketplace thủ công (`extraKnownMarketplaces` chỉ khai báo source, không auto-clone):

```bash
claude plugin marketplace add n24q02m/claude-plugins
```

Plugins bao gồm:

- **Code quality**: security-guidance, pr-review-toolkit, better-code-review-graph
- **Development**: feature-dev, frontend-design, superpowers, claude-md-management
- **LSP**: gopls, typescript, pyright, rust-analyzer
- **Browser**: playwright (Microsoft), chrome-devtools-mcp (browser automation, devtools)
- **MCP servers (n24q02m-plugins)**: wet-mcp, mnemo-mcp, better-notion-mcp, better-email-mcp, better-godot-mcp, better-telegram-mcp, better-code-review-graph
- **Marketplaces**: n24q02m-plugins (n24q02m/claude-plugins), cc-marketplace (kenryu42)

## Bước 4: Cài đặt skills

Skills được chia thành 2 loại:

### Custom skills (lưu trong repo này)

```bash
# Copy 4 custom skills
for skill in ai-ml fullstack-dev infra-devops product-growth; do
  cp -r skills/$skill ~/.claude/skills/$skill
done
```

### External skills (cài từ git)

```bash
# gstack (QA, browse, review, ship, retro, plan-review)
cd ~/.claude/skills && git clone https://github.com/garrytan/gstack.git
cd gstack && bun install

# Tạo symlinks/junctions cho sub-skills
# Trên macOS/Linux: dùng symlink
cd ~/.claude/skills
for skill in browse gstack-upgrade plan-ceo-review plan-eng-review qa qa-only retro review setup-browser-cookies ship; do
  ln -sf gstack/$skill $skill
done

# Trên Windows (Git Bash): dùng Windows junction (mklink /J)
# Symlink không hoạt động đúng trên Windows — git clone sẽ tạo copy thay vì link
cd ~/.claude/skills
for skill in browse gstack-upgrade plan-ceo-review plan-eng-review qa qa-only retro review setup-browser-cookies ship; do
  cmd //c "mklink /J C:\\Users\\$USER\\.claude\\skills\\$skill C:\\Users\\$USER\\.claude\\skills\\gstack\\$skill"
done

# claude-bug-bounty
cd ~/.claude/skills && git clone https://github.com/shuvonsec/claude-bug-bounty.git
```

## Bước 5: Cấu hình MCP Servers

MCP servers chia 2 nguồn:

- **Plugin MCP** (7 servers): Quản lý bởi `n24q02m-plugins` marketplace — tự động cài khi bật plugin trong `settings.json`. Credentials cấu hình qua `setup`/`config` tools của từng plugin.
- **Direct MCP** (3 servers): Cấu hình trong `~/.claude.json` (mục `mcpServers`). File `claude-code/mcp-servers.json` chứa template với placeholders.

```bash
# Merge direct MCP servers vào ~/.claude.json (cần jq)
jq -s '.[0] * {"mcpServers": .[1].mcpServers}' ~/.claude.json claude-code/mcp-servers.json > /tmp/claude-merged.json
mv /tmp/claude-merged.json ~/.claude.json
```

Thay thế các `<PLACEHOLDER>` bằng credentials thật:

| Placeholder | Mô tả | Nguồn |
|-------------|-------|-------|
| `<STITCH_API_KEY>` | Google Stitch API key | Google AI Studio |
| `<GRAFANA_URL>` | Grafana URL | Self-hosted |
| `<GRAFANA_TOKEN>` | Grafana service account token | Grafana Admin |

## Bước 5.5: VS Code Claude Agent + Gemini 3 Flash (2026 pivot)

GitHub Copilot tích hợp Claude Agent vào VS Code. Cấu hình để dùng Claude (Anthropic) hoặc Gemini 3 Flash (Google) tùy task.

### VS Code Settings

Thêm vào `settings.json` (Ctrl+Shift+P → "Open User Settings (JSON)"):

```json
{
  "github.copilot.chat.models": {
    "claude-3.5-sonnet": {
      "provider": "anthropic",
      "model": "claude-3.5-sonnet"
    },
    "claude-3.5-haiku": {
      "provider": "anthropic",
      "model": "claude-3.5-haiku"
    }
  }
}
```

### Smoke Test

1. Mở VS Code Command Palette → "GitHub Copilot: Open Chat"
2. Chọn model `claude-3.5-haiku` (Student tier: unlimited, 0x premium requests)
3. Gửi prompt đơn giản: "Write a hello world in Python"
4. Verify response từ Haiku (không phải GPT-4o)

### Gemini 3 Flash cho Paperclip VC

Paperclip Virtual Company trên infra-vnic dùng Gemini 3 Flash qua Hermes agent:

- API key: `GOOGLE_AI_STUDIO_API_KEY` (Doppler: virtual-company/dev)
- Model: `gemini-3.1-flash` (poor tier), `gemini-3.1-pro` (rich tier)
- Arena rank: #11 (tốt cho general tasks, giá rẻ)

Xem `virtual-company/settings.yaml` để config model routing.

## Bước 6: Cấu hình settings.local.json (tùy chọn)

File này chứa cài đặt riêng từng máy, KHÔNG đồng bộ:

```bash
cat > ~/.claude/settings.local.json << 'EOF'
{
  "outputStyle": "Explanatory",
  "prefersReducedMotion": true
}
EOF
```

Các tùy chọn khác: `"outputStyle"` có thể là `"Explanatory"`, `"Learning"`, hoặc bỏ trống.

## Bước 7: Cấu hình project-level MCP (tùy chọn)

MCP servers chỉ dùng cho 1 project cụ thể (VD: mobile-mcp cho ~/projects):

```bash
# Dùng Claude Code CLI
claude mcp add --scope project mobile-mcp -- bun x @mobilenext/mobile-mcp@latest
```

Hoặc chỉnh sửa trong `~/.claude.json` mục `projects.<path>.mcpServers`.

## Cấu trúc file

```
~/.claude/
  CLAUDE.md                  # Global instructions (đồng bộ)
  settings.json              # Plugins, permissions, env (đồng bộ)
  settings.local.json        # Machine-specific (KHÔNG đồng bộ)
  skills/                    # Skills (đồng bộ custom, clone external)
    ai-ml/                   # Custom
    fullstack-dev/            # Custom
    infra-devops/             # Custom
    product-growth/           # Custom
    claude-bug-bounty/        # External (git clone)
    gstack/                   # External (git clone)
    browse -> gstack/browse   # Symlink
    ...
  plugins/                   # Tự động quản lý bởi Claude Code
  projects/                  # Project-level memory (tự động)

~/.claude.json               # Global state + MCP servers (KHÔNG đồng bộ, chứa secrets)
```

## Cập nhật

Khi thay đổi config trên 1 máy, cập nhật repo:

```bash
cd ~/projects/n24q02m

# Cập nhật settings
cp ~/.claude/settings.json claude-code/settings.json

# Cập nhật CLAUDE.md
cp ~/.claude/CLAUDE.md claude-code/CLAUDE.md

# Cập nhật custom skills
for skill in ai-ml fullstack-dev infra-devops product-growth; do
  cp -r ~/.claude/skills/$skill skills/$skill
done

# Commit và push (chỉ dùng fix:/feat: prefix)
git add -A && git commit -m "feat: sync claude code config" && git push
```

Trên máy khác, pull và chạy lại Bước 2-4.

## Lưu ý

- **KHÔNG BAO GIỜ** commit `~/.claude.json` vì chứa credentials (API keys, tokens, passwords)
- **KHÔNG** commit `settings.local.json` (machine-specific)
- **KHÔNG** commit `~/.claude/plugins/` (tự động cài khi khởi động)
- **KHÔNG** commit `~/.claude/projects/` (project-level memory, auto-generated)
- Plugins tự động cài đặt khi khởi động Claude Code nếu đã khai báo trong `settings.json`
- External skills (gstack, claude-bug-bounty) cần cập nhật bằng `git pull` trong thư mục tương ứng

## Phụ lục: Thiết lập GitHub Copilot VS Code đồng bộ 100%

Để Copilot VSC có thể "tương tự và đầy đủ" sức mạnh và bối cảnh (context) giống như Claude Code, bạn cần áp dụng các thay đổi sau vào VS Code.

### Đồng bộ System Prompts

Trong `~/.config/Code - Insiders/User/prompts/` (hoặc `Code/User/prompts/`), hãy tạo file `AGENTS.instructions.md` với cùng nội dung:

```bash
mkdir -p "$HOME/.config/Code - Insiders/User/prompts/"
cp claude-code/CLAUDE.md "$HOME/.config/Code - Insiders/User/prompts/AGENTS.instructions.md"
```

### Đồng bộ Skills

Sao chép lại mô hình Skills và các thư viện external (Gstack) cho Copilot bằng cách đưa vào thư mục Prompts:

```bash
# 1. Custom skills
mkdir -p "$HOME/.config/Code - Insiders/User/prompts/skills"
for skill in ai-ml fullstack-dev infra-devops product-growth; do
  cp -r skills/$skill "$HOME/.config/Code - Insiders/User/prompts/skills/$skill"
done

# 2. External skills
cd "$HOME/.config/Code - Insiders/User/prompts/skills"
git clone https://github.com/garrytan/gstack.git
(cd gstack && bun install)

for skill in browse gstack-upgrade plan-ceo-review plan-eng-review qa qa-only retro review setup-browser-cookies ship; do
  ln -sf gstack/$skill $skill
done

git clone https://github.com/shuvonsec/claude-bug-bounty.git
```

### Đồng bộ MCP Servers & Permission

Sử dụng `settings.json` của VS Code (`~/.config/Code - Insiders/User/settings.json`) để thêm cấu hình bypass và định nghĩa list MCP servers:

```json
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.claudeAgent.allowDangerouslySkipPermissions": true,
  "github.copilot.chat.mcp.servers": {
    "wet": {"command": "uvx", "args": ["--python", "3.13", "wet-mcp@latest"]},
    "mnemo": {"command": "uvx", "args": ["--python", "3.13", "mnemo-mcp@latest"]},
    "better-notion": {"command": "bun", "args": ["x", "@n24q02m/better-notion-mcp@latest"]},
    "better-email": {"command": "bun", "args": ["x", "@n24q02m/better-email-mcp@latest"]},
    "better-godot": {"command": "bun", "args": ["x", "@n24q02m/better-godot-mcp@latest"]},
    "better-telegram": {"command": "uvx", "args": ["--python", "3.13", "better-telegram-mcp@latest"]},
    "better-code-review-graph": {"command": "uvx", "args": ["--python", "3.13", "better-code-review-graph@latest"]}
  }
```

*Ghi chú: Thêm các biến môi trường env/API KEY nếu cần thiết (tương tự như `~/.claude.json`).*
