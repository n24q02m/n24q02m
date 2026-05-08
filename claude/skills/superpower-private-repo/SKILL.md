---
name: superpower-private-repo
description: Quy tắc lưu trữ AI traces (.jules, superpower content) cho repo public và private. Mọi spec/plan/roadmap của repo public PHẢI lưu vào private repo `n24q02m/.superpower` (subfolder per public repo), KHÔNG lưu vào `docs/superpowers/` của public repo (kể cả gitignored). Sử dụng trước khi viết spec/plan cho repo public, hoặc khi phát hiện superpower content đã commit nhầm vào public repo.
when_to_use: writing spec/plan/roadmap/architecture for any public repo, auditing AI traces in repos, fixing accidental commit of superpower content to public repo
---

# superpower-private-repo

## Khi nào dùng

- Trước khi viết spec/plan/roadmap/migration cho bất kỳ public repo nào.
- Khi audit AI traces (`.jules`, `.superpower`, `superpowers`, `docs/superpowers`) trong repo.
- Khi phát hiện superpower content đã bị commit vào repo public (lỗi cần cleanup).

## Quy tắc

### Repo PUBLIC (trong list https://github.com/stars/n24q02m/lists/productions)

**BẮT BUỘC**:
1. `.gitignore` phải có:
   ```
   .jules/
   .Jules/
   .jules
   .superpower/
   superpower/
   superpowers/
   docs/superpowers/
   ```

2. **TUYỆT ĐỐI KHÔNG TẠO** các thư mục trên trong public repo, kể cả local untracked. Lý do: rủi ro leak khi `git add -A`, hoặc khi `git rm --cached` chưa được chạy, hoặc developer khác clone repo về vô tình add.

3. **Spec/plan/roadmap cho public repo X** phải lưu tại:
   ```
   ~/projects/.superpower/<X>/specs/YYYY-MM-DD-<topic>.md
   ~/projects/.superpower/<X>/plans/YYYY-MM-DD-<topic>.md
   ```
   - Repo private: `n24q02m/.superpower`
   - Local clone: `C:\Users\n24q02m-wlap\projects\.superpower\` (Windows) / `~/projects/.superpower/` (Unix)
   - Mỗi public repo có subfolder riêng: `.superpower/skret/`, `.superpower/claude-plugins/`, `.superpower/better-godot-mcp/`, v.v.

4. **KHÔNG** lưu tại `~/projects/<X>/docs/superpowers/` cho public repo X.

### Repo PRIVATE

- `.jules` vẫn phải gitignore (artifact của AI agent, không nên track).
- `superpower` (vd `docs/superpowers/`) **được phép** tồn tại + track trong repo private (vd `oci-vm-infra`, `oci-vm-prod`, `virtual-company`).

### Rotation fallback

Nếu cần stash spec/plan nhanh khi `.superpower/` chưa sync hoặc unreachable, dùng tạm trong:
- `~/projects/oci-vm-infra/docs/superpowers/`
- `~/projects/oci-vm-prod/docs/superpowers/`
- `~/projects/virtual-company/docs/superpowers/`

Cả 3 đều là private repo. Sau đó migrate về `.superpower/<X>/` khi tiện.

## Workflow trước khi viết spec/plan cho public repo X

1. `ls ~/projects/.superpower/<X>/` — verify subfolder tồn tại. Nếu chưa: `mkdir -p ~/projects/.superpower/<X>/{specs,plans}`.
2. Save file vào path đúng: `~/projects/.superpower/<X>/specs/YYYY-MM-DD-<topic>.md`.
3. KHÔNG tạo `~/projects/<X>/docs/superpowers/` ở public repo X.
4. Reference path trong spec/plan dùng absolute path: `~/projects/.superpower/<X>/...` để tránh hiểu nhầm.

## Audit existing repos

Để check có superpower content đã lỡ commit vào public repo:

```bash
for repo in ~/projects/<list-public-repos>; do
  cd $repo
  if git ls-files --error-unmatch docs/superpowers/ 2>/dev/null; then
    echo "VIOLATION: $repo has tracked docs/superpowers/"
  fi
done
```

## Cleanup nếu đã lỡ commit

**Phát hiện** qua `git ls-files docs/superpowers/` trả về files (≠ empty).

**KHÔNG** tự rewrite history. **BẮT BUỘC** báo user + đề xuất 2 options:

### Option A — `git rm --cached` + commit (đơn giản, file vẫn trong history)

```bash
cd ~/projects/<public-repo>
git rm --cached -r docs/superpowers/
git commit -m "fix: untrack docs/superpowers from public repo per security rule"
git push
```

Pros: nhanh, không destructive.
Cons: file vẫn nằm trong git history (`git log -- docs/superpowers/`), bất kỳ ai pull về có thể see history.

### Option B — BFG repo-cleaner purge + force push (xoá permanent, destructive)

```bash
cd /tmp
git clone --mirror git@github.com:n24q02m/<public-repo>.git
cd <public-repo>.git
java -jar bfg.jar --delete-folders 'superpowers' --no-blob-protection
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

Pros: xoá permanent, không trace.
Cons: rewrite history, ALL collaborators phải re-clone, signed commits sẽ break, có thể conflict với forks/PRs đang open. Cần user EXPLICIT approve.

**KHÔNG** được defer "fix sau" (vi phạm rule `CẤM ĐỂ FIX SAU`).

## Lịch sử

- 2026-04-18: skret repo phát hiện 7 file đã committed public từ 2026-04-05 đến 2026-04-12 (`docs/superpowers/specs/*` + `docs/superpowers/plans/*`). User chọn Option A → commit `9034db6` untrack.
- Skret 2 file mới hôm nay (2026-04-18) đã catch + save thẳng vào `.superpower/skret/` tránh vi phạm.
