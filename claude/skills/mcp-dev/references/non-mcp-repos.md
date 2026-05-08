# Non-MCP Repos Sanity Check (Configs #21-24)

File này bổ sung cho `e2e-full-matrix.md` ở bốn cấu hình cuối cùng (#21-24). Bốn repo non-MCP không có mode matrix và không có relay flow, nhưng vẫn phải verify trước khi Phase 4 release. Mỗi repo có tập sanity check riêng; không dùng chung checklist với 20 MCP configs.

Scope bốn repo:
- `qwen3-embed` (config #21) — Python lib embedding + reranker
- `web-core` (config #22) — Python shared web infra (SearXNG runner)
- `claude-plugins` (config #23) — marketplace cho 7 MCP server
- `n24q02m` profile (config #24) — public sync target của `~/.claude/`

Nguyên tắc: tất cả sanity check phải chạy trực tiếp với user (không background), clean workspace trước, ghi timestamp từng check.

## qwen3-embed (config #21)

Language: Python. Role: embedding + reranker library. No relay flow.

### Checks

- [ ] Clean workspace:
  ```bash
  cd ~/projects/qwen3-embed
  git status  # expect clean or only expected local changes
  uv sync
  ```

- [ ] Run full test suite:
  ```bash
  uv run pytest tests/ --tb=short -v
  ```
  Expected: all tests pass (exit 0). Note any skipped tests (usually GPU-only).

- [ ] Import smoke — embedding:
  ```bash
  uv run python -c "
  from qwen3_embed import Qwen3Embedder
  e = Qwen3Embedder()
  result = e.embed(['hello world', 'foo bar'])
  print('shape:', result.shape)
  assert result.shape[0] == 2
  print('PASS')
  "
  ```
  Expected: shape `(2, N)` where N = embedding dim, prints "PASS".

- [ ] Import smoke — reranker:
  ```bash
  uv run python -c "
  from qwen3_embed import Qwen3Reranker
  r = Qwen3Reranker()
  scores = r.score('find Python tutorial', ['Python docs', 'Rust book', 'JS guide'])
  print('scores:', scores)
  assert len(scores) == 3
  print('PASS')
  "
  ```
  Expected: list of 3 floats (higher = better match), prints "PASS".

### Gate

All 4 checks must pass. Record results with timestamps.

## web-core (config #22)

Language: Python. Role: shared web infra (SearXNG runner, Docker fallback). No relay flow.

### Checks

- [ ] Clean workspace:
  ```bash
  cd ~/projects/web-core
  git status
  uv sync
  ```

- [ ] Run full test suite:
  ```bash
  uv run pytest tests/ --tb=short -v
  ```
  Expected: all tests pass.

- [ ] SearXNG Docker runner alive check:
  ```bash
  uv run python -m web_core.searxng.runner --check
  ```
  Expected output contains "SearXNG ready at http://127.0.0.1:8888" (or configured port).
  Side effect: temporarily starts Docker container. Teardown happens automatically after check.

- [ ] Verify SearXNG is accessible during check:
  ```bash
  # While runner is up (or in parallel window)
  curl -sf http://127.0.0.1:8888/healthz || curl -sf http://127.0.0.1:8888/
  ```
  Expected: HTTP 200.

- [ ] Teardown verification:
  ```bash
  # After --check returns, container should be stopped
  docker ps --filter "ancestor=searxng/searxng" --format "{{.ID}}"
  ```
  Expected: empty output (no leaked containers).

### Gate

All 5 checks must pass. Record Docker container lifecycle timestamps.

## claude-plugins (config #23)

Role: marketplace for 7 MCP servers. Language: JSON + JavaScript lint scripts.

### Checks

- [ ] Clean workspace:
  ```bash
  cd ~/projects/claude-plugins
  git status
  ```

- [ ] Validate each plugin.json via jq:
  ```bash
  fail_count=0
  for p in plugins/*/plugin.json; do
    if ! jq empty "$p" 2>/dev/null; then
      echo "FAIL: $p (invalid JSON)"
      fail_count=$((fail_count + 1))
    fi
  done
  echo "Total failures: $fail_count"
  ```
  Expected: `Total failures: 0`.

- [ ] Run marketplace lint script:
  ```bash
  node scripts/lint-marketplace.js
  echo "exit: $?"
  ```
  Expected: `exit: 0` (no schema violations, no orphan plugins).

- [ ] Dry-run install each MCP plugin:
  ```bash
  fail_count=0
  for plugin in better-notion-mcp better-email-mcp better-telegram-mcp wet-mcp mnemo-mcp better-code-review-graph better-godot-mcp; do
    if ! claude plugin install "$plugin" --dry-run 2>/dev/null; then
      echo "FAIL: $plugin"
      fail_count=$((fail_count + 1))
    fi
  done
  echo "Total install failures: $fail_count"
  ```
  Expected: `Total install failures: 0`.

- [ ] Verify each plugin.json references correct repo URLs and versions:
  ```bash
  for p in plugins/*/plugin.json; do
    name=$(jq -r '.name' "$p")
    repo=$(jq -r '.repository' "$p")
    version=$(jq -r '.version' "$p")
    echo "$name -> $repo @ $version"
  done
  ```
  Expected: all 7 MCP plugins listed with `n24q02m/` repo prefix.

### Gate

All 5 checks must pass.

## n24q02m profile (config #24)

Role: public sync target of `~/.claude/` (CLAUDE.md + skills + agents + commands). Markdown only.

### Checks

- [ ] Clean workspace:
  ```bash
  cd ~/projects/n24q02m
  git status
  ```

- [ ] Markdown lint:
  ```bash
  npx markdownlint-cli '**/*.md' --ignore node_modules --ignore .git
  echo "exit: $?"
  ```
  Expected: `exit: 0` (or documented violations).

- [ ] Broken link check (CLAUDE.md + README.md):
  ```bash
  npx markdown-link-check -q CLAUDE.md
  npx markdown-link-check -q README.md
  ```
  Expected: all links reachable.

- [ ] Secret scan (local grep — fast layer before GitHub secret-scanning):
  ```bash
  grep -rE "GOCSPX-[a-zA-Z0-9_-]+|sk-[a-zA-Z0-9]{40,}|100\.[0-9]+\.[0-9]+\.[0-9]+|@outlook\.com|@klprism\.com|SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}" . \
    --include="*.md" --include="*.json" --include="*.yml" --include="*.yaml" \
    --exclude-dir=node_modules --exclude-dir=.git \
    | grep -vE "placeholder|example|<.*>|docs/examples/" \
    | head -20
  ```
  Expected: no matches (all inline values should be placeholders per `feedback_claude_md_public_sync.md`).

- [ ] Verify CLAUDE.md references valid skills:
  ```bash
  # Extract skill invocations, verify each exists
  grep -oE 'Skill [a-z][a-z-]*' CLAUDE.md | sort -u | while read line; do
    name=$(echo "$line" | awk '{print $2}')
    if [[ -d "$HOME/.claude/skills/$name" ]]; then
      echo "  $name: EXISTS"
    else
      echo "  $name: MISSING"
    fi
  done
  ```
  Expected: all referenced skills exist.

- [ ] Verify MEMORY.md index links to valid memory files (if synced — usually NOT since memory is local-only):
  ```bash
  # Memory should NOT be in profile repo per rule feedback_claude_md_public_sync.md
  ls .claude/projects 2>/dev/null && echo "BAD: memory syncs publicly - violation" || echo "OK: no memory in profile repo"
  ```
  Expected: `OK: no memory in profile repo`.

### Gate

All 6 checks must pass. Secret-scan MUST be zero (hardest gate — violation means public leak).

## Aggregate Gate

Configs #21-24 all green, combined with configs #1-20 from `e2e-full-matrix.md` → Phase 3 ALL GREEN (24/24). Chỉ khi đủ 24/24 mới chuyển sang Phase 4 release dispatch.

Ghi rõ timestamp từng config + exit code từng check vào session log. Nếu 1 config fail → Phase 3 KHÔNG green, quay về Phase 1 fix root cause theo recovery path bên dưới.

## Failure Recovery

- **qwen3-embed test fail** → back to Phase 1, fix via real commit (không patch local workspace). Re-run config #21 sau khi fix merge vào main.
- **web-core Docker runner leak** → manual cleanup trước khi retry:
  ```bash
  docker ps -a --filter "ancestor=searxng/searxng" -q | xargs -r docker rm -f
  ```
  Sau đó re-run config #22. Nếu leak tái diễn → bug trong `web_core.searxng.runner` teardown path, back to Phase 1.
- **claude-plugins invalid JSON / lint fail** → back to Phase 1, fix schema. Re-run config #23 sau khi merge.
- **n24q02m secret detected** → IMMEDIATE escalation, KHÔNG tiếp tục Phase 3:
  1. Rotate credential bị leak (theo loại: OAuth client secret / API key / phone).
  2. Purge khỏi git history: `git filter-repo --path <file> --invert-paths` hoặc theo guide của `feedback_claude_md_public_sync.md`.
  3. Force-push main (user approve trước).
  4. Notify downstream dependants nếu có.
  5. Sau khi clean history + GitHub secret-scanning alert resolved → re-run config #24.

Mọi recovery đều phải quay về Phase 1 (fix root cause + commit), không patch workspace local rồi qua Phase 3.

## Cross-references

- `e2e-full-matrix.md` — configs #21-24 summary row (non-MCP section).
- `feedback_claude_md_public_sync.md` — profile repo secret rule, escalation protocol.
- `scope-and-repos.md` — role của từng non-MCP repo trong scope 12 repos.
- `mode-matrix.md` — chỉ áp dụng configs #1-20 (7 MCP servers). Non-MCP repos không có mode matrix.
