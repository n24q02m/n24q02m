# repo-bootstrap

Read-side bootstrap scripts for n24q02m repo standards (Spec G1).

## Scripts

| Script | Purpose |
|---|---|
| `audit.py` | 6-medium GitHub-detail audit (30 checks across 9 groups). Read-only via `gh` CLI. |
| `verify.py` | CI gate: re-runs audit + 4 wiring checks (pre-commit hook + CD job + CODEOWNERS + ci.yml). |
| `verify_readme_sync.py` | Per-language registry README field check (PyPI/npm/Cargo/Dockerfile + universal + MCP). |
| `promo_sync.py` | Cross-repo promo block sync from Productions Stars list (14 public repos). |

## Quick start

```bash
# Audit a repo
python scripts/repo-bootstrap/audit.py --repo=n24q02m/skret

# Local verify (run from inside any repo)
cd ~/projects/skret
python ~/projects/n24q02m/scripts/repo-bootstrap/verify.py

# Per-language README sync check
python ~/projects/n24q02m/scripts/repo-bootstrap/verify_readme_sync.py --repo-root=.

# Cross-promo sync (dry-run)
python scripts/repo-bootstrap/promo_sync.py --dry-run
```

## Output formats

All four scripts accept `--format=table` (default human) / `--format=json` / `--format=markdown`.

## Composite actions (CI reuse)

Consumer repos invoke via:

```yaml
- uses: n24q02m/n24q02m/.github/actions/repo-bootstrap-audit@main
- uses: n24q02m/n24q02m/.github/actions/repo-bootstrap-verify@main
- uses: n24q02m/n24q02m/.github/actions/repo-bootstrap-promo-sync@main
```

See `.github/actions/repo-bootstrap-*/action.yml` for input/output specs.

## Dependencies

Pure stdlib (Python 3.13+). External tools required at runtime:
- `gh` CLI authenticated (`gh auth status` shows logged in)
- `git` CLI (for `verify.py` repo auto-detection)

No `requirements.txt` / `pyproject.toml` deps — scripts run via `python script.py` directly.

## Tests

```bash
pip install pytest
python -m pytest scripts/repo-bootstrap/tests/ -v
```

## Architecture

Shared utilities live in `_lib.py`:
- `GhClient` — subprocess wrapper around `gh api` with response cache
- `Tier` enum + `detect_tier(repo)` from Stars list
- `CheckResult` dataclass + `@check(group, name)` decorator + global registry
- `format_table` / `format_json` / `format_markdown` output helpers
- `extract_readme_tagline` / `normalize_for_match` parsing helpers

Each check function returns `CheckResult(group, name, status, message, evidence)`. Status is `PASS` / `FAIL` / `SKIP`. Tier-aware checks SKIP for the wrong tier with a clear message.

## Spec G2 (deferred)

Write-side scripts (`init.py`, `apply.py`) and full bootstrap templates per language are tracked in Spec G2 — separate brainstorm + plan cycle.
