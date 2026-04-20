# Backlog Allowlist

**Updated**: 2026-04-20
**Scope**: 12 repos (see `scope-and-repos.md`)
**Purpose**: Define which open issues/PRs are permitted during EMPTY BACKLOG gate (Phase 0 of mcp-dev cascade).

## Auto-allowed (bot-generated, no manual entry required)

1. **Renovate Dependency Dashboard** — exactly 1 per repo.
   - Title pattern (regex, case-insensitive): `Dependency Dashboard`
   - Created by: Renovate bot (`renovate[bot]`)
   - Long-lived by design (Renovate updates checklist in-place).
   - Audit script auto-filters via jq `select(.title | test("Dependency Dashboard"; "i") | not)`.

No other auto-allowed categories.

## Explicit allowlist (require user approval)

Each entry must have: repo, issue #, title, type, reason, date added, review-by date.

| Repo | # | Title | Type | Reason | Added | Review-by |
|---|---|---|---|---|---|---|

_(rows populated per cascade session when user approves specific long-running issues)_

### Allowed types
- `long-running` — work spans multiple sessions, actively tracked
- `upstream-blocked` — waiting for external dep (framework, library, platform)
- `roadmap` — explicit quarterly/yearly roadmap item, not actionable now
- `user-education` — kept as FAQ / reference for users

### NOT allowed types (must close or fix)
- `bug` — fix now or dismiss as not-a-bug
- `security` — handled via Dependabot/CodeQL/secret-scanning, strict zero
- `feature-request without commitment` — close with "tracked in roadmap" response

## Strict zero (no allowlist permitted, must be 0 at gate)

- **Dependabot alerts** (all severities) — fix or dismiss with reason (false positive, not-applicable, tolerable-risk). Cross-ref `feedback_google_oauth_desktop_public.md` for specific dismissal patterns.
- **CodeQL alerts** — same as above.
- **Secret-scanning alerts** — rotate credential + dismiss with `revoked`.
- **Open PRs** — merge with real review (`backlog-clearance.md`) or close with explicit reason (out-of-scope, superseded, invalid).

## How to add entry

1. **User explicitly approves** a long-running issue to keep open:
   > "giữ issue #NNN repo X, lý do Y, review-by Z"
2. Add row to table above with all 7 columns.
3. Commit + push profile repo `n24q02m` (public sync).
4. Re-run audit script; gate should now pass for that issue.

## How to expire entry

- When `Review-by` date passes (or is ≤ today): user must re-justify or close issue.
- Expired without action: next cascade blocks gate until resolved.
- `Review-by` date typically 3 months out; max 6 months.

## How to close entry

When work completes:
1. Close GitHub issue with explanation.
2. Remove row from this allowlist file.
3. Commit + push profile repo.

## Example entry (illustrative — not current state)

```
| mcp-core | #789 | Migrate to Edge runtime for relay server | long-running | Q3 2026 roadmap, blocks=nothing critical | 2026-04-20 | 2026-07-01 |
| wet-mcp | #234 | Support Yandex search API | upstream-blocked | Yandex API v2 pending public release | 2026-04-20 | 2026-06-01 |
```

## Cross-references

- Audit script reads from this file: `audit-commands.md` (jq filter for explicit entries).
- Gate formula: `audit-commands.md` section "Gate formula".
- Violation context: `feedback_work_order_fix_test_release.md` (EMPTY BACKLOG gate origin).
- Security alert dismissal: `feedback_google_oauth_desktop_public.md`.
