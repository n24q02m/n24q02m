# PR/Issue Review — 6-item Checklist

BẮT BUỘC đọc TRƯỚC KHI merge/close/approve any PR or issue, đặc biệt bot PRs (Jules/Sentinel/Bolt/Daisy/Renovate/Dependabot).

## 6-item checklist

1. **Full diff** từng file/hunk cross-check scope với title
2. **PR + inline review comments** (`gh pr view <N> --comments` + `gh api repos/<r>/pulls/<N>/comments`) — reviewer concerns, request-changes, unresolved threads
3. **Linked issues** qua `closingIssuesReferences` → `gh issue view <M> --comments` đọc bug context + user priority
4. **CI run logs** nếu UNSTABLE/FAILING (`gh run view <id> --log-failed`) — failure có thể reveal scope creep
5. **Commit messages** của PR để hiểu decision rationale
6. **Scope map** diff vs title, flag xoá file/revert feature/đổi default

## Verdicts

- Diff chứa changes ngoài scope HOẶC comments có unresolved concerns → REJECT + tách PR
- Bot PRs (Jules/Sentinel/Bolt) thường kèm collateral damage — extra scrutiny

## Anti-patterns CẤM

- "Backlog cleanup quick merge"
- Skip comments
- Admin flag bypass failing CI

## Bulk-close rule

KHÔNG bulk close issues thuộc loại Epic / Feature Request / Roadmap tracking để đạt "EMPTY BACKLOG gate". Triage vào `backlog-allowlist.md` với user approval.

## Violation

2026-04-19: Jules PR #517 title `[FIX] Missing Cache` nhưng diff revert remote-oauth mode + xoá `src/auth/notion-token-store.ts` → phá mode matrix notion.

Memory: `feedback_pr_review_must_be_real.md` + `feedback_never_bulk_close.md`.
