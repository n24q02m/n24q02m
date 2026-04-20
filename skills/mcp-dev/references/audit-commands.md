# Audit Commands — EMPTY BACKLOG gate (Phase 0 mcp-dev cascade)

Script chuẩn tắc dùng cho **Phase 0 backlog audit** trong mcp-dev cascade (fix → test → release).
Gate này quyết định: có được phép tiến sang Phase 2 (clean state) + Phase 3 (E2E) hay không.

**Khi nào chạy**: đầu session multi-repo có scope "làm đầy đủ / fix all / audit all / ready for E2E / ready to release". Chạy LẠI sau mỗi lần clear 1 item trong Phase 1 (backlog clearance).

**Cross-ref**:
- Scope 12 repo: `./scope-and-repos.md` + memory `scope-12-repos.md`
- Gate formula nguồn: memory `feedback_work_order_fix_test_release.md`
- `--limit 1000` rule: memory `feedback_gh_cli_pagination.md`

---

## 12-repo scope reminder

Audit BẮT BUỘC cover đủ 12 repo (không 7, không 8, không 11):

| # | Repo | Role |
|---|------|------|
| 1 | `mcp-core` | Shared MCP primitives (core-ts + core-py) |
| 2 | `better-notion-mcp` | MCP server — Notion (remote OAuth) |
| 3 | `better-email-mcp` | MCP server — Email (remote relay) |
| 4 | `better-telegram-mcp` | MCP server — Telegram (remote relay) |
| 5 | `wet-mcp` | MCP server — Web toolkit (local relay) |
| 6 | `mnemo-mcp` | MCP server — Memory (local relay) |
| 7 | `better-code-review-graph` | MCP server — Code graph (local relay) |
| 8 | `better-godot-mcp` | MCP server — Godot (local non-relay) |
| 9 | `qwen3-embed` | Embedding/reranker lib |
| 10 | `web-core` | Shared web infra package |
| 11 | `claude-plugins` | Marketplace cho better-* MCP |
| 12 | `n24q02m` | Profile repo (public sync `~/.claude/`) |

Nếu scope audit ≠ 12 repo → STOP, confirm user explicit narrow scope trước khi chạy.

---

## Full audit script

Lưu thành `audit.sh` rồi `bash audit.sh`. Output = per-repo metric line + aggregate gate verdict.

```bash
#!/usr/bin/env bash
# mcp-dev Phase 0 backlog audit — 12 repos
# Usage: bash audit.sh
# Output: per-repo metric line + aggregate gate verdict

set -u
REPOS=(
  mcp-core
  better-notion-mcp better-email-mcp better-telegram-mcp
  wet-mcp mnemo-mcp better-code-review-graph
  better-godot-mcp
  qwen3-embed web-core claude-plugins n24q02m
)

# Load explicit allowlist from backlog-allowlist.md
# Format expected: | repo | #NNN | Title | Type | Reason | Added | Review-by |
ALLOWLIST_FILE=~/.claude/skills/mcp-dev/references/backlog-allowlist.md
declare -A ALLOWED_ISSUES
if [[ -f "$ALLOWLIST_FILE" ]]; then
  while IFS= read -r line; do
    # Match | <repo> | #<N> | ...
    if [[ "$line" =~ \|[[:space:]]+([a-z0-9-]+)[[:space:]]+\|[[:space:]]+#([0-9]+) ]]; then
      repo="${BASH_REMATCH[1]}"
      num="${BASH_REMATCH[2]}"
      ALLOWED_ISSUES["$repo"]+="$num "
    fi
  done < "$ALLOWLIST_FILE"
fi

TOTAL_PRS=0
TOTAL_ISSUES_UNALLOWED=0
TOTAL_SECURITY=0
GATE_FAIL=0

for repo in "${REPOS[@]}"; do
  prs=$(gh pr list -R n24q02m/$repo --state open --limit 1000 --json number --jq 'length' 2>/dev/null || echo 0)

  issues_raw=$(gh issue list -R n24q02m/$repo --state open --limit 1000 --json number,title 2>/dev/null || echo '[]')
  issues_total=$(echo "$issues_raw" | jq 'length')

  # Filter: exclude Dependency Dashboard (Renovate auto-allow) + explicit allowlist
  allowed_list="${ALLOWED_ISSUES[$repo]:-}"
  issues_unallowed=$(echo "$issues_raw" | jq --arg allowed "$allowed_list" '
    [.[]
     | select(.title | test("Dependency Dashboard"; "i") | not)
     | select(.number as $n | ($allowed | split(" ") | map(tonumber? // empty) | index($n)) | not)
    ] | length')

  deps=$(gh api "repos/n24q02m/$repo/dependabot/alerts" --paginate --jq '[.[] | select(.state=="open")] | length' 2>/dev/null | awk '{s+=$1} END {print s+0}')
  codeql=$(gh api "repos/n24q02m/$repo/code-scanning/alerts?state=open&per_page=100" --paginate --jq 'length' 2>/dev/null | awk '{s+=$1} END {print s+0}')
  secret=$(gh api "repos/n24q02m/$repo/secret-scanning/alerts?state=open&per_page=100" --paginate --jq 'length' 2>/dev/null | awk '{s+=$1} END {print s+0}')

  security_total=$((deps + codeql + secret))
  TOTAL_PRS=$((TOTAL_PRS + prs))
  TOTAL_ISSUES_UNALLOWED=$((TOTAL_ISSUES_UNALLOWED + issues_unallowed))
  TOTAL_SECURITY=$((TOTAL_SECURITY + security_total))

  status=""
  if (( prs > 0 || issues_unallowed > 0 || security_total > 0 )); then
    status="  BLOCK"
    GATE_FAIL=1
  fi

  printf "%-26s PRs=%-3d issues=%d/%d (unallowed/total) deps=%d codeql=%d secret=%d%s\n" \
    "$repo" "$prs" "$issues_unallowed" "$issues_total" "$deps" "$codeql" "$secret" "$status"
done

echo
echo "=== AGGREGATE ==="
echo "Total open PRs: $TOTAL_PRS"
echo "Total unallowed issues: $TOTAL_ISSUES_UNALLOWED"
echo "Total security alerts: $TOTAL_SECURITY"
echo
if (( GATE_FAIL == 0 )); then
  echo "GATE: PASS — proceed to Phase 2 (clean state) + Phase 3 (E2E)"
else
  echo "GATE: FAIL — return to Phase 1 (backlog clearance)"
  exit 1
fi
```

---

## Gate formula

```
gate_pass = (TOTAL_PRS == 0)
          AND (TOTAL_ISSUES_UNALLOWED == 0)
          AND (TOTAL_SECURITY == 0)
```

3 điều kiện này AND với nhau. Bất kỳ điều kiện nào > 0 → **GATE: FAIL** → quay lại Phase 1 (backlog clearance).

`TOTAL_SECURITY = dependabot_open + codeql_open + secret_scanning_open` trên toàn 12 repo. KHÔNG có ngoại lệ "severity low skip" — rule memory `feedback_work_order_fix_test_release.md` yêu cầu **0 tuyệt đối**.

`TOTAL_ISSUES_UNALLOWED` = open issues trừ đi 2 nhóm:
1. Title match `Dependency Dashboard` (Renovate auto-generated, không phải backlog thật).
2. Issue # nằm trong allowlist file `backlog-allowlist.md` (roadmap tracking, user explicit approved giữ mở).

---

## Rule: `--limit 1000` bắt buộc

Nguồn: memory `feedback_gh_cli_pagination.md`.

Default limits gây miss items → sai metric → false "clean":

| Command | Default | Đúng |
|---|---|---|
| `gh pr list` | 30 | `--limit 1000` |
| `gh issue list` | 30 | `--limit 1000` |
| `gh run list` | 20 | `--limit 1000` |
| `gh release list` | 30 | `--limit 1000` |

**Red flag**: khi thấy count = 30 hoặc 20 → NGHI TRUNCATE → re-run với `--limit 1000`. Nếu count > 1000 (hiếm) → switch sang `gh api --paginate`.

Cross-ref: memory `feedback_gh_cli_pagination.md` (rule gốc từ session 4739cb45, user nhắc "đừng có bao giờ dùng gh cli mặc định để lấy list").

---

## Per-repo drill-down commands

Khi audit script FAIL 1 repo, chạy các command sau để investigate chi tiết (thay `<repo>` bằng tên repo bị block):

```bash
# List open PRs with titles + authors
gh pr list -R n24q02m/<repo> --state open --limit 1000 --json number,title,author,createdAt

# List open issues (with labels để phân loại roadmap vs actionable)
gh issue list -R n24q02m/<repo> --state open --limit 1000 --json number,title,labels,createdAt

# List open dependabot alerts (severity + package + manifest)
gh api "repos/n24q02m/<repo>/dependabot/alerts" --paginate | jq '.[] | select(.state=="open") | {id: .number, severity: .security_advisory.severity, pkg: .dependency.package.name, path: .dependency.manifest_path}'

# List open code-scanning alerts (rule + file path)
gh api "repos/n24q02m/<repo>/code-scanning/alerts?state=open&per_page=100" --paginate | jq '.[] | {id: .number, rule: .rule.id, severity: .rule.severity, file: .most_recent_instance.location.path}'

# List open secret-scanning alerts (secret type + resolution)
gh api "repos/n24q02m/<repo>/secret-scanning/alerts?state=open&per_page=100" --paginate | jq '.[] | {id: .number, type: .secret_type, resolved: .resolution}'
```

Với mỗi item trả về → quyết định action:
- **PR**: đọc FULL diff (rule `feedback_pr_review_must_be_real.md`) → merge / close với lý do / request changes.
- **Issue**: fix / close as duplicate / add to allowlist (nếu roadmap tracking với user approval).
- **Security alert**: patch dependency / fix code / rotate secret / dismiss với justification (VD Google OAuth Desktop public client — memory `feedback_google_oauth_desktop_public.md`).

---

## How to use

1. **Phase 0 (đầu session multi-repo)**: copy script ra `audit.sh`, chạy `bash audit.sh`.
2. **Nếu GATE: PASS** → tiếp Phase 2 (clean state: xoá config.enc + token cache + session lock mọi server) + Phase 3 (E2E clean-state relay flow).
3. **Nếu GATE: FAIL** → vào Phase 1 (`backlog-clearance.md`): clear theo priority order (Security Sentinel > Dependabot > Bot PRs > Renovate > Open issues).
4. **Sau mỗi item clear xong** → re-run audit script ngay. KHÔNG accumulate rồi audit 1 lần cuối (dễ miss item mới phát sinh).
5. **Chỉ khi GATE: PASS liên tiếp 2 lần** (lần 1 sau clearance + lần xác nhận) → mới chuyển Phase 2.

**Anti-patterns cấm**:
- Chạy audit subset (8 / 11 repo) rồi claim "all clean" — phải đủ 12.
- Bỏ `--limit 1000` → default 30 → miss PRs → false pass.
- Skip security alerts ("severity low, không blocking") — rule = 0 tuyệt đối.
- Release dispatch khi GATE FAIL (vi phạm `feedback_work_order_fix_test_release.md`).
