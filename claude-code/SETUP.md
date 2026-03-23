# Claude Code Setup Guide

Huong dan thiet lap Claude Code tren may moi de dong bo voi cau hinh hien tai.

## Yeu cau

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (>= 2.1.x)
- [bun](https://bun.sh/) (chay MCP servers TypeScript)
- [uv](https://docs.astral.sh/uv/) (chay MCP servers Python)
- Python 3.13 (pinned cho moi Python MCP server)
- [mise](https://mise.jdx.dev/) (quan ly runtime versions)

## Buoc 1: Clone repo

```bash
git clone https://github.com/n24q02m/n24q02m.git ~/projects/n24q02m
cd ~/projects/n24q02m
```

## Buoc 2: Copy global CLAUDE.md

```bash
cp claude-code/CLAUDE.md ~/.claude/CLAUDE.md
```

File nay chua cac quy tac chung ap dung cho moi project (ngon ngu, chuan muc code, security).

## Buoc 3: Copy settings.json

```bash
cp claude-code/settings.json ~/.claude/settings.json
```

File nay chua:
- **Plugins**: Danh sach plugins duoc bat (official + marketplace)
- **Marketplaces**: Cac marketplace ben thu ba (cc-marketplace, code-review-graph)
- **Env vars**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`
- **Permissions**: `bypassPermissions` mode

Sau khi copy, khoi dong Claude Code de plugins tu dong cai dat.

Plugins bao gom:
- **Code quality**: security-guidance, pr-review-toolkit, code-review-graph, safety-net
- **Development**: feature-dev, frontend-design, superpowers, claude-md-management
- **LSP**: gopls, typescript, pyright, rust-analyzer
- **Browser**: playwright (Microsoft), chrome-devtools-mcp (browser automation, devtools)
- **Marketplaces**: cc-marketplace (kenryu42), code-review-graph (tirth8205)

## Buoc 4: Cai dat skills

Skills duoc chia thanh 2 loai:

### Custom skills (luu trong repo nay)

```bash
# Copy 4 custom skills
for skill in ai-ml fullstack-dev infra-devops product-growth; do
  cp -r skills/$skill ~/.claude/skills/$skill
done
```

### External skills (cai tu git)

```bash
# gstack (QA, browse, review, ship, retro, plan-review)
cd ~/.claude/skills && git clone https://github.com/gstack-so/gstack.git
cd gstack && bun install

# Tao symlinks cho sub-skills
cd ~/.claude/skills
for skill in browse gstack-upgrade plan-ceo-review plan-eng-review qa qa-only retro review setup-browser-cookies ship; do
  ln -sf gstack/$skill $skill
done

# claude-bug-bounty
cd ~/.claude/skills && git clone https://github.com/anthropics/claude-bug-bounty.git
```

## Buoc 5: Cau hinh MCP Servers

MCP servers duoc cau hinh trong `~/.claude.json` (muc `mcpServers`). File `claude-code/mcp-servers.json` chua template voi placeholders.

```bash
# Xem template
cat claude-code/mcp-servers.json
```

Sau do dung Claude Code de them tung server:

```bash
# Hoac copy truc tiep vao ~/.claude.json (can jq)
jq -s '.[0] * {"mcpServers": .[1].mcpServers}' ~/.claude.json claude-code/mcp-servers.json > /tmp/claude-merged.json
mv /tmp/claude-merged.json ~/.claude.json
```

Thay the cac `<PLACEHOLDER>` bang credentials that:

| Placeholder | Mo ta | Nguon |
|-------------|-------|-------|
| `<STITCH_API_KEY>` | Google Stitch API key | Google AI Studio |
| `<TELEGRAM_API_ID>` | Telegram API ID | my.telegram.org |
| `<TELEGRAM_API_HASH>` | Telegram API hash | my.telegram.org |
| `<TELEGRAM_PHONE>` | So dien thoai Telegram | -- |
| `<GOOGLE_API_KEY>` | Google AI API key | Google AI Studio |
| `<COHERE_API_KEY>` | Cohere API key | dashboard.cohere.com |
| `<GITHUB_TOKEN>` | GitHub PAT (fine-grained) | GitHub Settings |
| `<GRAFANA_URL>` | Grafana URL | Self-hosted |
| `<GRAFANA_TOKEN>` | Grafana service account token | Grafana Admin |

## Buoc 6: Cau hinh settings.local.json (tuy chon)

File nay chua cai dat rieng tung may, KHONG dong bo:

```bash
cat > ~/.claude/settings.local.json << 'EOF'
{
  "outputStyle": "Explanatory",
  "prefersReducedMotion": true
}
EOF
```

Cac tuy chon khac: `"outputStyle"` co the la `"Explanatory"`, `"Learning"`, hoac bo trong.

## Buoc 7: Cau hinh project-level MCP (tuy chon)

MCP servers chi dung cho 1 project cu the (VD: mobile-mcp cho ~/projects):

```bash
# Dung Claude Code CLI
claude mcp add --scope project mobile-mcp -- bun x @mobilenext/mobile-mcp@latest
```

Hoac chinh sua trong `~/.claude.json` muc `projects.<path>.mcpServers`.

## Cau truc file

```
~/.claude/
  CLAUDE.md                  # Global instructions (dong bo)
  settings.json              # Plugins, permissions, env (dong bo)
  settings.local.json        # Machine-specific (KHONG dong bo)
  skills/                    # Skills (dong bo custom, clone external)
    ai-ml/                   # Custom
    fullstack-dev/            # Custom
    infra-devops/             # Custom
    product-growth/           # Custom
    claude-bug-bounty/        # External (git clone)
    gstack/                   # External (git clone)
    browse -> gstack/browse   # Symlink
    ...
  plugins/                   # Tu dong quan ly boi Claude Code
  projects/                  # Project-level memory (tu dong)

~/.claude.json               # Global state + MCP servers (KHONG dong bo, chua secrets)
```

## Cap nhat

Khi thay doi config tren 1 may, cap nhat repo:

```bash
cd ~/projects/n24q02m

# Cap nhat settings
cp ~/.claude/settings.json claude-code/settings.json

# Cap nhat CLAUDE.md
cp ~/.claude/CLAUDE.md claude-code/CLAUDE.md

# Cap nhat custom skills
for skill in ai-ml fullstack-dev infra-devops product-growth; do
  cp -r ~/.claude/skills/$skill skills/$skill
done

# Commit va push
git add -A && git commit -m "chore: sync claude code config" && git push
```

Tren may khac, pull va chay lai Buoc 2-4.

## Luu y

- **KHONG BAO GIO** commit `~/.claude.json` vi chua credentials (API keys, tokens, passwords)
- **KHONG** commit `settings.local.json` (machine-specific)
- **KHONG** commit `~/.claude/plugins/` (tu dong cai khi khoi dong)
- **KHONG** commit `~/.claude/projects/` (project-level memory, auto-generated)
- Plugins tu dong cai dat khi khoi dong Claude Code neu da khai bao trong `settings.json`
- External skills (gstack, claude-bug-bounty) can cap nhat bang `git pull` trong thu muc tuong ung
