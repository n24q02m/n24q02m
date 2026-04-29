# Release Cascade — Phase 4-5 Dispatch Protocol

Phase 4-5 của mcp-dev cascade. **CHỈ bước vào sau khi Phase 3 (E2E full matrix) show 19/19 green** (post-imagine-mcp 2026-04-24). Release dispatch là **LAST action của session** — không có exception, không release giữa chừng.

Nếu Phase 3 còn bất kỳ config nào chưa PASS → QUAY LẠI fix, KHÔNG được dispatch. Nếu session còn bất kỳ PR/issue/security alert nào open trên TẤT CẢ 13 repo trong scope → QUAY LẠI `backlog-allowlist.md`, KHÔNG được dispatch.

**Per-release gate (2026-04-29)**: Phase 3 E2E gate áp dụng cho MỌI release dispatch — bao gồm baseline release, addendum, hotfix, patch trên cùng đợt. Không có "đã E2E ở Wave 6 rồi, addendum chỉ cần unit test → ship". Vi phạm session `rollback-d18-plugin-daemon` 2026-04-29: skip E2E sau Wave 9-11 D17/D18 addendum → ship `mcp-core 1.11.3` với D18 spam tabs P0. Xem `e2e-full-matrix.md` "E2E PER RELEASE" + memory `feedback_e2e_per_release_strict.md`.

Cross-ref: `feedback_work_order_fix_test_release.md` (FIX → TEST → RELEASE bất biến), `feedback_test_before_release.md` (merge trước, E2E trên main, release cuối), `feedback_e2e_per_release_strict.md` (E2E per release).

---

## Dispatch order (strict)

```
Phase 4 dispatch sequence:

  1. mcp-core (stable)                    <-- MUST be first; downstream pin source
      |
      |  wait + verify: new tag, PyPI n24q02m-mcp-core published, npm @n24q02m/mcp-core published
      |  verify: downstream auto-issues created in 8 MCP + 3 consumer repos
      |
      v
  2. 8 MCP servers (parallel OK):
      - better-notion-mcp
      - better-email-mcp
      - better-telegram-mcp
      - wet-mcp
      - mnemo-mcp
      - better-code-review-graph
      - better-godot-mcp
      - imagine-mcp
      |
      |  wait + verify: each repo has new release tag
      |
      v
  3. Downstream consumers (if changed since last release):
      - qwen3-embed
      - web-core
      - claude-plugins (marketplace refresh)
      |
      v
  4. Profile repo (n24q02m) — if CLAUDE.md/skills/agents changed
      |
      v
  Done → enter Phase 5 verify
```

**Tại sao mcp-core phải đi ĐẦU**: tất cả 8 MCP server + 3 downstream consumer pin `@n24q02m/mcp-core` hoặc `n24q02m-mcp-core`. Nếu release 8 MCP trước khi mcp-core stable mới lên registry → MCP server lock vào version cũ, bỏ qua bugfix vừa ship trong session. Lặp lại vi phạm 2026-04-17 (session 80d829f6) khi cut mcp-core v1.1.1 xong mới phát hiện OAuth bug → phải bump v1.1.2 + cascade lại.

**Tại sao 8 MCP OK parallel**: không repo nào pin repo MCP khác. Dispatch 8 workflow simultaneously giảm wall-clock time từ ~70 min xuống ~15 min.

---

## PSR auto-version rule

**TUYỆT ĐỐI KHÔNG** manual `git tag v1.2.3` hoặc manual release note. Tất cả release đi qua CD workflow:

```bash
# Stable release — PSR đọc commit history, tính version, tag, publish
gh workflow run cd.yml -R n24q02m/<repo> -f stable=true
```

**PSR behavior** (python-semantic-release cho Python, semantic-release cho TS):
- `fix:` commit → patch bump (v1.2.3 → v1.2.4)
- `feat:` commit → minor bump (v1.2.3 → v1.3.0)
- `feat!:` / `BREAKING CHANGE:` footer → major bump (v1.2.3 → v2.0.0)

Dự án này dùng **chỉ `fix:` + `feat:`** theo `feedback_commit_prefix.md` → max bump per commit là minor. Major bump yêu cầu user approval EXPLICIT.

Cross-ref `feedback_psr_auto_version.md`: KHÔNG tự pick version trong spec/plan/PR. Version là OUTPUT của PSR, KHÔNG phải input.

---

## Downstream auto-issue verification (Phase 5 part 1)

Sau khi mcp-core stable cut, verify tracking issues đã được tạo ở 10 downstream repo:

```bash
CORE_VERSION=$(gh release view --repo n24q02m/mcp-core --json tagName --jq .tagName)
echo "Just released mcp-core $CORE_VERSION"

for repo in better-notion-mcp better-email-mcp better-telegram-mcp wet-mcp mnemo-mcp better-code-review-graph better-godot-mcp imagine-mcp qwen3-embed web-core claude-plugins; do
  count=$(gh issue list -R n24q02m/$repo --search "bump mcp-core $CORE_VERSION" --state open --limit 5 --json number --jq 'length')
  if [[ $count -gt 0 ]]; then
    echo "  $repo: OK ($count tracking issue(s) found)"
  else
    echo "  $repo: MISSING — mcp-core CD workflow may have failed to create issue"
  fi
done
```

Nếu repo nào thiếu tracking issue:
- Check `mcp-core/.github/workflows/cd.yml` có step `auto-issue-downstream` chưa
- Check exit code của step đó trong workflow run log: `gh run view <run-id> -R n24q02m/mcp-core --log`
- Manual tạo nếu CD fail:
  ```bash
  gh issue create -R n24q02m/<repo> \
    --title "chore: bump mcp-core to $CORE_VERSION" \
    --body "Release: https://github.com/n24q02m/mcp-core/releases/tag/$CORE_VERSION"
  ```

Cross-ref `feedback_core_release_auto_issue.md` — consumer list: 7 MCP + KP + downstream apps + embedding daemon consumers.

---

## Per-release post-dispatch verify (Phase 5 part 2)

Chờ ~10 min sau mỗi dispatch, chạy verify function:

```bash
verify_release() {
  local repo=$1

  echo ">>> Verifying release for $repo"

  # 1. New release tag exists
  local tag
  tag=$(gh release view --repo n24q02m/$repo --json tagName,publishedAt --jq '[.tagName, .publishedAt] | @tsv')
  echo "  release tag: $tag"

  # 2. Publish to registry
  case "$repo" in
    mcp-core)
      # Both PyPI + npm
      pip index versions n24q02m-mcp-core 2>/dev/null | head -3
      npm view @n24q02m/mcp-core version
      ;;
    wet-mcp|mnemo-mcp|better-code-review-graph|better-telegram-mcp|qwen3-embed|web-core)
      # Python packages
      local pypi_name
      case "$repo" in
        better-code-review-graph) pypi_name="better-code-review-graph" ;;
        better-telegram-mcp) pypi_name="better-telegram-mcp" ;;
        *) pypi_name="$repo" ;;
      esac
      pip index versions "$pypi_name" 2>/dev/null | head -3
      ;;
    better-notion-mcp|better-email-mcp|better-godot-mcp)
      # TypeScript npm packages
      npm view "@n24q02m/$repo" version
      ;;
    claude-plugins)
      # Marketplace — no registry, verify via gh release only
      ;;
  esac

  # 3. Docker image (for remotely deployed servers)
  case "$repo" in
    better-notion-mcp|better-email-mcp|better-telegram-mcp)
      # These deploy to OCI VM via Docker
      gh api "repos/n24q02m/$repo/packages" 2>/dev/null | jq '.[].package_type' | head -5
      ;;
  esac

  # 4. CF Pages deploy green (for docs/plugins)
  case "$repo" in
    claude-plugins|n24q02m)
      echo "  (verify CF Pages deployment via dashboard manually)"
      ;;
  esac
}

# Usage
verify_release mcp-core
verify_release wet-mcp
# ... repeat for all 12 repos dispatched
```

---

## Detect downstream changes since last release

Step 3 của dispatch order chỉ chạy cho repo có commit mới kể từ last tag:

```bash
check_downstream_commits() {
  for repo in qwen3-embed web-core claude-plugins; do
    last_tag=$(gh release view --repo n24q02m/$repo --json tagName --jq .tagName 2>/dev/null || echo "")
    if [[ -z "$last_tag" ]]; then
      echo "$repo: no prior release — FIRST RELEASE, dispatch required"
      continue
    fi
    commits=$(gh api "repos/n24q02m/$repo/compare/$last_tag...main" --jq '.commits | length' 2>/dev/null || echo 0)
    echo "$repo: $commits commits since $last_tag"
    if (( commits > 0 )); then
      echo "  -> dispatch required"
    fi
  done
}
```

Nếu `commits == 0` cho repo nào → SKIP dispatch, không force release rỗng (PSR sẽ báo "no release needed" và fail workflow → noise).

---

## Downstream pin bump PR verification (Phase 5 part 3)

Sau mcp-core release + tracking issue, mỗi downstream repo nên có Renovate PR hoặc manual PR bump pin. Verify:

```bash
for repo in better-notion-mcp better-email-mcp better-telegram-mcp wet-mcp mnemo-mcp better-code-review-graph better-godot-mcp imagine-mcp; do
  pr_count=$(gh pr list -R n24q02m/$repo --search "bump mcp-core" --state open --limit 5 --json number --jq 'length')
  echo "$repo: $pr_count bump PR(s) open"
done
```

**Expected**: mỗi repo có PR open HOẶC issue open (PR sẽ follow từ Renovate run trong vài giờ). Cả hai cùng absent = downstream drift risk — manual intervene.

---

## Anti-patterns cấm

1. **Release mid-session** — chỉ Phase 4 sau 24/24 green. Vi phạm 2026-04-17 session 80d829f6: release crg v3.9.1, godot v1.12.1, telegram v4.5.0, email v1.22.5, mnemo v1.20.1, wet v2.25.1, mcp-core v1.1.1 giữa chừng → downstream pin outdated + OAuth bug release xong mới fix → phải bump v1.1.2 re-cascade. Cross-ref `feedback_work_order_fix_test_release.md`.

2. **Incremental per-repo release** — release TẤT CẢ 12 trong cùng Phase 4, KHÔNG "release 1 now, test more, release 2 later". Test gap giữa các release = uncontrolled version skew.

3. **Manual tag creation** — `git tag v1.2.3 && git push --tags` FORBIDDEN. PSR only. Vi phạm session 25/03 (wet-mcp manual tag v2.16.0) → bỏ qua PyPI publish + Docker build + CHANGELOG → phải delete + recreate + wasted 30 min. Cross-ref `feedback_psr_release.md`.

4. **Release với `file:` pin to local mcp-core** — test với published version, KHÔNG local path. Vi phạm 2026-04-18 session 4739cb45: propose "E2E với file: pin trên branch trước khi merge" → không reflect thực tế. Cross-ref `feedback_test_before_release.md`.

5. **Skip downstream auto-issue verify** — leads to pin drift trong N tuần. Vi phạm 2026-04-17: sau mcp-core v1.1.1 + v1.1.2, better-godot-mcp vẫn pin `^1.0.0`, better-telegram-mcp vẫn `>=1.1.0`.

6. **Test only default mode then release** — phải 19/19 full matrix pass (15 MCP configs + 4 non-MCP). Cross-ref `e2e-full-matrix.md`.

7. **Manual pick version number** — spec/plan/PR/issue KHÔNG được đề xuất `v0.1.0`, `v1.0.0`. Dùng `<auto>` / `<next-version>` / `<computed>`. Cross-ref `feedback_psr_auto_version.md`.

---

## Rollback protocol

PSR là **forward-only**. Nếu post-release phát hiện bug:

- **KHÔNG** `gh release delete <tag>` — phá registry + downstream pin reference + PSR state.
- **DO** bump to next patch với `fix:` commit address bug:

```bash
cd ~/projects/<repo>
git checkout main
git pull
# ... fix code ...
git add <files>
git commit -m "fix: address <bug-description> in <released-version>"
git push
gh workflow run cd.yml -R n24q02m/<repo> -f stable=true
```

Nếu bug breaking cho downstream: tạo issue ở mọi consumer repo giải thích + suggested pin bump.

---

## Exit criteria for Phase 4

Phase 4 chỉ được mark complete khi tất cả điều kiện sau đạt:

- [ ] All 10 repo trong scope (mcp-core + 7 MCP + qwen3-embed + web-core + claude-plugins) đã dispatch (hoặc explicit skip với reason "no commits since last tag").
- [ ] Mỗi release verified: tag exists, registry published (PyPI/npm cho repo có package), Docker image built cho remotely deployed servers.
- [ ] Downstream auto-issue created cho TẤT CẢ 10 consumer repo (từ mcp-core CD step).
- [ ] Downstream pin bump PR open ở ≥ 7/7 MCP repo (hoặc issue tracking nếu Renovate chưa chạy).
- [ ] Phase 5 verification commands all green.
- [ ] Session task #4 (release cascade) marked completed.

---

## Cross-references

- `feedback_work_order_fix_test_release.md` — FIX → TEST → RELEASE bất biến, empty backlog gate trước E2E
- `feedback_psr_auto_version.md` — KHÔNG manual pick, dùng placeholder `<auto>`
- `feedback_psr_release.md` — PSR workflow, never manual tag
- `feedback_core_release_auto_issue.md` — downstream tracking issue rule, consumer list per core
- `feedback_test_before_release.md` — merge trước (private repos không auto-CD), E2E trên main, release cuối
- `feedback_commit_prefix.md` — chỉ `fix:` và `feat:`, không `!` (no major auto-bump)
- `backlog-allowlist.md` — empty backlog gate (precondition cho Phase 3)
- `e2e-full-matrix.md` — 24/24 config full matrix (precondition cho Phase 4)
