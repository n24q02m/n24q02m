# Backlog Clearance — Phase 1 Protocol

Phase 1 của mcp-dev cascade. Được kích hoạt khi **Phase 0 audit gate FAIL** (xem `audit-commands.md`).
Thoát Phase 1 khi re-audit PASS (PRs=0, issues=0 ngoài allowlist, security alerts=0, cred rotations=0 trên toàn bộ 12 repos trong scope).

**Nguyên tắc nền**: Mỗi PR/issue được xử lý **THẬT** — đọc full diff, user approve từng item, không bulk close, không dispatch subagent auto-merge.

## 1. Priority Order (strict sequence)

Xử lý theo đúng thứ tự dưới đây. KHÔNG nhảy bước — security alert còn mở thì chưa đụng đến renovate.

1. **Security alerts**
   - Sentinel CRITICAL/HIGH PRs (bot mở PR fix vulnerability)
   - Dependabot alerts (`gh api repos/<repo>/dependabot/alerts --jq '[.[] | select(.state=="open")]'`)
   - CodeQL / secret-scanning alerts đang open
   - Credential rotation pending (Google OAuth Web, AWS IAM access keys, CF token, v.v.)
2. **Bot PRs** (extra scrutiny — xem case study section 5)
   - Bolt (performance optimization)
   - Daisy / Jules (test / fix / cache / cleanup)
   - Custom `[SECURITY]` tags
   - Jules **đặc biệt nguy hiểm** — thường rebase trên old main, kèm collateral damage
3. **Renovate dependency PRs**
   - Batch update PRs, review theo group per ecosystem (npm, pip, uv, actions)
   - Verify lockfile + package.json cùng update, không skew version
4. **Open issues**
   - Actionable ngay → fix trong session (tạo PR với commit `fix:` hoặc `feat:`)
   - Long-running / upstream-blocked → triage vào `backlog-allowlist.md` (cần user approval)
   - Stale / irrelevant → close với comment giải thích

## 2. Per-PR Review Protocol (sequential, interactive)

Mỗi PR đi qua **9 bước**, user approve trước khi execute. **Bước 1-6 = đọc đủ context; Bước 7 = quyết định; Bước 8 = execute; Bước 9 = verify.**

### Step 1 — Đọc metadata
```bash
gh pr view <N> -R n24q02m/<repo>
```
Lấy title, description, labels, author (bot hay human), base branch, CI status.

### Step 2 — Đọc FULL diff
```bash
gh pr diff <N> -R n24q02m/<repo>
```
Đọc **từng file, từng hunk**. Không scroll qua, không dừng ở file đầu.

### Step 3 — Đọc PR comments + inline review comments
```bash
gh pr view <N> -R n24q02m/<repo> --comments
gh api repos/n24q02m/<repo>/pulls/<N>/comments  # inline review comments
```
Scan mọi thread cho: reviewer request-changes, user pushback, unresolved concerns, bot retry messages (Jules/Renovate có thể retry với update scope). Nếu thread có unresolved issue → flag.

### Step 4 — Đọc linked issues (nếu có "Closes #X")
```bash
gh pr view <N> -R n24q02m/<repo> --json closingIssuesReferences
# For each linked issue:
gh issue view <M> -R n24q02m/<repo> --comments
```
Hiểu bug gốc, user priority, repro steps. PR có giải quyết HẾT issue không hay chỉ partial? Partial fix → comment yêu cầu scope rõ ràng hoặc close issue với explanation.

### Step 5 — Đọc CI run logs nếu UNSTABLE/FAILING
```bash
gh pr checks <N> -R n24q02m/<repo>
gh run view <failing-run-id> -R n24q02m/<repo> --log-failed | tail -80
```
Fail log có thể reveal: lint fail ở file không-liên-quan (= drive-by change), test timeout reveals race condition, security scan fail reveals hidden risk. **KHÔNG** dùng `--admin` flag bypass failing CI nếu chưa đọc log hiểu root cause.

### Step 6 — Cross-check scope + Extra scrutiny cho bot PR
Build mental map: title nói "fix X" → diff chạm các file Y, Z, W → các file đó có nằm trong scope X không?
Nếu có file/hunk **ngoài scope**, hoặc comments có unresolved concerns, hoặc CI fail vì scope creep → flag ngay.

Bot PR checklist (Jules/Sentinel/Bolt/Daisy):
- [ ] Có xóa file nào không? Đặc biệt `src/auth/*`, `src/transports/*`, `config.py`, `setup.py`
- [ ] Có đổi default value / mode / entry point không?
- [ ] Có revert feature mode gần đây không? (check `git log` cho các file bị touch)
- [ ] PR được rebase trên current main hay stale branch? `gh pr view <N> --json baseRefOid` rồi compare với `main` HEAD
- [ ] Có touch files critical ngoài scope claim không? (transport, config, auth, registry)
- [ ] Comments thread có reviewer/user comment "please split" hoặc "not what I want"?

### Step 7 — User approval per PR
**BẮT BUỘC** present findings (diff summary + comments summary + linked issues + CI status) cho user, chờ decision explicit: **merge / close / request-split / skip**.
KHÔNG tự quyết, KHÔNG dispatch subagent để auto-close.

### Step 8 — Execute decision
- **Merge** (prefer squash cho clean history):
  ```bash
  gh pr merge <N> -R n24q02m/<repo> --squash --delete-branch
  ```
- **Close with reason**:
  ```bash
  gh pr close <N> -R n24q02m/<repo> --comment "Reason: <lý do cụ thể>"
  ```
- **Request split** (comment + close, yêu cầu author tách):
  ```bash
  gh pr comment <N> -R n24q02m/<repo> --body "Scope creep: diff chứa <X> ngoài title. Please split into: (1) <X>, (2) <original scope>."
  gh pr close <N> -R n24q02m/<repo>
  ```

### Step 9 — Post-action verification
- Merge → `git log main --oneline -1 -R <repo>` shows new commit SHA + prefix `fix:` hoặc `feat:` (xem `feedback_commit_prefix.md` — **không bao giờ** `chore:`/`refactor:`/`docs:`/`ci:`/`build:`/`style:`/`perf:`/`test:`)
- Close → `gh pr list -R <repo> --state closed --limit 5` shows PR này đã closed
- Re-run audit snippet cho repo → PR count giảm đúng 1

## 3. Anti-patterns (STOP ngay nếu bắt gặp suy nghĩ này)

- **"CI green = safe to merge"** — CI verify build + test, KHÔNG verify scope. Jules PR #517 CI green nhưng revert remote-oauth mode.
- **"Backlog quick merge cleanup"** — mỗi PR cần real review. "Quick merge để reach gate" = vi phạm gate purpose.
- **"Title says X, merge without reading diff"** — title lies, diff doesn't. Luôn đọc diff.
- **"Bot PR automatically safe"** — SAI. Jules #517 là case study chính.
- **"Bulk close N PRs để reach gate nhanh hơn"** — cấm tuyệt đối (xem `feedback_never_bulk_close.md`).
- **"Dispatch agent auto-close/auto-merge"** — cấm (xem `feedback_pr_review_process.md`).
- **"Tôi nhớ PR này chỉ fix X"** — memory không đủ, phải đọc lại diff trực tiếp.
- **"Diff sạch nên skip comments"** — SAI. Comments có thể chứa reviewer concerns chưa resolve, user override scope, hidden constraints.
- **"CI fail nhưng unrelated, admin-merge bypass"** — SAI. Luôn đọc `--log-failed` trước, fail log có thể reveal scope creep.
- **"Issue title đã nói rồi, không cần đọc thread"** — SAI. Comments reveal repro, priority, related incidents.

## 4. Jules PR #517 Case Study (2026-04-19)

Vi phạm thực tế — dùng làm reference cho mọi bot PR sau này.

| Field | Value |
|---|---|
| Title | `[FIX] Missing Cache` |
| Author | `google-labs-jules[bot]` |
| Claimed scope | Workspace bot info caching |
| Actual diff (15 files) | Legit: `workspace.ts`, `workspace.test.ts` (cache logic). **OUT OF SCOPE**: `transports/http.ts` revert từ 130 lines (remote-oauth dual-mode) xuống 85 lines (local-relay only), xóa `src/auth/notion-token-store.ts`, revert `config.ts` → `setup.ts`, revert `registry.ts` |
| Outcome | Auto-merge không review → phá mode matrix (notion default `http remote oauth` mất) → regression phát hiện ở E2E staging khi crash `NOTION_OAUTH_CLIENT_ID required` |
| Fix | Revert PR #517 phần out-of-scope, keep workspace cache (legit) |
| Lesson | **NEVER merge bot PRs on title alone. Diff is source of truth.** |

## 5. Verification per PR Action

Xác nhận action đã THẬT SỰ có tác dụng, không dừng ở exit code.

### Sau Merge
```bash
git -C <repo-local-path> pull origin main
git -C <repo-local-path> log --oneline -1
# Kỳ vọng: commit SHA mới, message bắt đầu bằng `fix:` hoặc `feat:`
```
Nếu prefix sai (ví dụ `chore:`, `refactor:`) → merge commit vi phạm `feedback_commit_prefix.md` → revert + re-merge đúng prefix.

### Sau Close
```bash
gh pr list -R n24q02m/<repo> --state closed --limit 5
```
PR phải xuất hiện trong closed list với timestamp gần đây.

### Re-audit
Chạy lại snippet từ `audit-commands.md` cho repo đó → PR count giảm đúng 1.

## 6. Issue Triage Decision Tree

```
Issue mới mở ra
├── Actionable ngay trong session?
│   └── YES → Fix (tạo PR với `fix:` hoặc `feat:` commit, follow Phase 1 PR protocol)
├── Long-running / upstream-blocked (litellm, authlib CVE, v.v.)?
│   └── YES → Add to `backlog-allowlist.md` với user approval + lý do + trigger-to-revisit
├── Security issue?
│   └── Strict: PHẢI fix trong session HOẶC dismiss qua proper channel (CVE waiver, false positive note)
│   └── KHÔNG defer "để session sau" (xem `feedback_never_defer_tasks.md`)
└── Stale / irrelevant?
    └── Close với comment: "Closing as <reason>. Reopen nếu <condition>."
```

**Quan trọng**: bug / security issue phát hiện trong session hiện tại PHẢI fix ngay, KHÔNG note "fix sau" / "Phase M.2" / "next cycle".

## 7. Exit Criteria Phase 1 → quay về Phase 0 re-audit

Phase 1 complete khi tất cả điều kiện sau đồng thời true:
- [ ] Toàn bộ open PRs đã processed (merged / closed với reason)
- [ ] Toàn bộ security alerts đã processed (fixed / dismissed qua proper channel)
- [ ] Toàn bộ open issues đã processed (fixed / allowlisted / closed)
- [ ] Toàn bộ cred rotations pending = 0
- [ ] Re-run `audit-commands.md` → **GATE PASS** trên tất cả 12 repos trong scope

Nếu gate vẫn FAIL sau khi tưởng Phase 1 xong → xem lại xem PR/issue nào miss, quay lại Step 1 cho item đó.

## 8. Cross-references

| File | Mục đích |
|---|---|
| `audit-commands.md` | Script detect backlog counts (Phase 0 + re-audit) |
| `backlog-allowlist.md` | Khi nào allowlist issue / PR + template |
| `feedback_pr_review_must_be_real.md` | Bot PR case studies (Jules #517 chi tiết) |
| `feedback_commit_prefix.md` | Commit message rules (`fix:` / `feat:` only) |
| `feedback_pr_review_process.md` | Interactive process, no agent dispatch |
| `feedback_never_bulk_close.md` | Rule tuyệt đối không bulk close |
| `feedback_work_order_fix_test_release.md` | Full work order: FIX → TEST → RELEASE |
| `mode-matrix.md` | Verify bot PR có phá default mode không |
| `config-parity.md` | Verify bot PR có phá category parity không |
