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
- **Permissions**: `auto` mode (tự động approve action an toàn, hỏi xác nhận cho action nguy hiểm)
- **Effort**: `high` (reasoning effort mặc định)

Sau khi copy, khởi động Claude Code để plugins tự động cài đặt.

Plugins bao gồm:
- **Code quality**: security-guidance, pr-review-toolkit, code-review-graph
- **Development**: feature-dev, frontend-design, superpowers, claude-md-management
- **LSP**: gopls, typescript, pyright, rust-analyzer
- **Browser**: playwright (Microsoft), chrome-devtools-mcp (browser automation, devtools)
- **Marketplaces**: n24q02m-plugins (n24q02m/n24q02m-plugins — 7 MCP plugins), cc-marketplace (kenryu42)

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
cd ~/.claude/skills && git clone https://github.com/gstack-so/gstack.git
cd gstack && bun install

# Tạo symlinks cho sub-skills
cd ~/.claude/skills
for skill in browse gstack-upgrade plan-ceo-review plan-eng-review qa qa-only retro review setup-browser-cookies ship; do
  ln -sf gstack/$skill $skill
done

# claude-bug-bounty
cd ~/.claude/skills && git clone https://github.com/anthropics/claude-bug-bounty.git
```

## Bước 5: Cấu hình MCP Servers

MCP servers được cấu hình trong `~/.claude.json` (mục `mcpServers`). File `claude-code/mcp-servers.json` chứa template với placeholders.

```bash
# Xem template
cat claude-code/mcp-servers.json
```

Sau đó dùng Claude Code để thêm từng server:

```bash
# Hoặc copy trực tiếp vào ~/.claude.json (cần jq)
jq -s '.[0] * {"mcpServers": .[1].mcpServers}' ~/.claude.json claude-code/mcp-servers.json > /tmp/claude-merged.json
mv /tmp/claude-merged.json ~/.claude.json
```

Thay thế các `<PLACEHOLDER>` bằng credentials thật:

| Placeholder | Mô tả | Nguồn |
|-------------|-------|-------|
| `<STITCH_API_KEY>` | Google Stitch API key | Google AI Studio |
| `<TELEGRAM_API_ID>` | Telegram API ID | my.telegram.org |
| `<TELEGRAM_API_HASH>` | Telegram API hash | my.telegram.org |
| `<TELEGRAM_PHONE>` | Số điện thoại Telegram | -- |
| `<GOOGLE_API_KEY>` | Google AI API key | Google AI Studio |
| `<COHERE_API_KEY>` | Cohere API key | dashboard.cohere.com |
| `<GITHUB_TOKEN>` | GitHub PAT (fine-grained) | GitHub Settings |
| `<GRAFANA_URL>` | Grafana URL | Self-hosted |
| `<GRAFANA_TOKEN>` | Grafana service account token | Grafana Admin |

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

# Commit và push
git add -A && git commit -m "chore: sync claude code config" && git push
```

Trên máy khác, pull và chạy lại Bước 2-4.

## Lưu ý

- **KHÔNG BAO GIỜ** commit `~/.claude.json` vì chứa credentials (API keys, tokens, passwords)
- **KHÔNG** commit `settings.local.json` (machine-specific)
- **KHÔNG** commit `~/.claude/plugins/` (tự động cài khi khởi động)
- **KHÔNG** commit `~/.claude/projects/` (project-level memory, auto-generated)
- Plugins tự động cài đặt khi khởi động Claude Code nếu đã khai báo trong `settings.json`
- External skills (gstack, claude-bug-bounty) cần cập nhật bằng `git pull` trong thư mục tương ứng
