#!/usr/bin/env python3
"""CI gate verifier — re-runs audit + checks pre-commit/CD wiring.

Usage (from any repo's working directory):
    python verify.py [--repo=auto] [--format=table]

Compared to audit.py, verify.py:
- Operates from a local repo checkout (reads .pre-commit-config.yaml,
  .github/workflows/cd.yml from disk).
- Adds 4 wiring checks specific to CI integration readiness.
- Returns the same CheckResult format; exit 1 if any FAIL.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import (  # type: ignore[import-not-found]
    CheckResult,
    GhError,
    Tier,
    has_failure,
    render_results,
    write_counts_file,
)
from audit import run_audit  # type: ignore[import-not-found]


def _detect_repo_from_git(repo_root: Path) -> str | None:
    """Read remote 'origin' URL via git, parse owner/name."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    # Patterns: git@github.com:owner/name.git OR https://github.com/owner/name.git
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", out)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def check_precommit_has_verify_readme_sync(repo_root: Path) -> CheckResult:
    cfg = repo_root / ".pre-commit-config.yaml"
    if not cfg.exists():
        return CheckResult(
            "Wiring", "precommit_has_verify_readme_sync", "FAIL",
            ".pre-commit-config.yaml not found",
        )
    content = cfg.read_text(encoding="utf-8")
    if "verify-readme-sync" in content or "verify_readme_sync" in content:
        return CheckResult(
            "Wiring", "precommit_has_verify_readme_sync", "PASS",
            "Hook reference found in .pre-commit-config.yaml",
        )
    return CheckResult(
        "Wiring", "precommit_has_verify_readme_sync", "FAIL",
        "No verify_readme_sync hook in .pre-commit-config.yaml",
    )


def check_cd_has_verify_readme_sync_job(repo_root: Path) -> CheckResult:
    cd = repo_root / ".github" / "workflows" / "cd.yml"
    if not cd.exists():
        return CheckResult(
            "Wiring", "cd_has_verify_readme_sync_job", "FAIL",
            ".github/workflows/cd.yml not found",
        )
    content = cd.read_text(encoding="utf-8")
    if "verify-readme-sync" in content or "repo-bootstrap-verify" in content:
        return CheckResult(
            "Wiring", "cd_has_verify_readme_sync_job", "PASS",
            "verify_readme_sync job referenced in cd.yml",
        )
    return CheckResult(
        "Wiring", "cd_has_verify_readme_sync_job", "FAIL",
        "No verify-readme-sync / repo-bootstrap-verify in cd.yml",
    )


def check_codeowners_has_admin(repo_root: Path) -> CheckResult:
    co = repo_root / ".github" / "CODEOWNERS"
    if not co.exists():
        return CheckResult(
            "Wiring", "codeowners_has_admin", "FAIL",
            ".github/CODEOWNERS not found",
        )
    content = co.read_text(encoding="utf-8")
    # Look for any global pattern '* @<user-or-team>'
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        m = re.match(r"\*\s+(@\S+)", line)
        if m:
            return CheckResult(
                "Wiring", "codeowners_has_admin", "PASS",
                f"Global owner: {m.group(1)}",
            )
    return CheckResult(
        "Wiring", "codeowners_has_admin", "FAIL",
        "No global pattern '* @owner' in CODEOWNERS",
    )


def check_ci_uses_repo_bootstrap_verify(repo_root: Path) -> CheckResult:
    ci = repo_root / ".github" / "workflows" / "ci.yml"
    if not ci.exists():
        return CheckResult(
            "Wiring", "ci_uses_repo_bootstrap_verify", "FAIL",
            ".github/workflows/ci.yml not found",
        )
    content = ci.read_text(encoding="utf-8")
    if "n24q02m/n24q02m/.github/actions/repo-bootstrap-verify" in content:
        return CheckResult(
            "Wiring", "ci_uses_repo_bootstrap_verify", "PASS",
            "ci.yml uses repo-bootstrap-verify composite action",
        )
    return CheckResult(
        "Wiring", "ci_uses_repo_bootstrap_verify", "FAIL",
        "ci.yml does not invoke n24q02m/.../repo-bootstrap-verify@main",
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CI gate verifier (audit + wiring checks)")
    p.add_argument(
        "--repo", default="auto",
        help="owner/name; 'auto' detects from git remote (default)",
    )
    p.add_argument("--format", default="table", choices=["json", "table", "markdown"])
    p.add_argument("--tier", choices=["1", "2"])
    p.add_argument("--repo-root", default=".", help="Local repo root (default: cwd)")
    p.add_argument("--output-file")
    p.add_argument("--counts-file")
    p.add_argument("--skip-audit", action="store_true",
                   help="Skip audit checks; only run wiring checks (faster)")
    return p.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    repo = args.repo
    if repo == "auto":
        detected = _detect_repo_from_git(repo_root)
        if not detected:
            print("ERROR: Could not detect repo from git remote. Pass --repo=owner/name", file=sys.stderr)
            return 2
        repo = detected

    force_tier = None
    if args.tier == "1":
        force_tier = Tier.TIER_1
    elif args.tier == "2":
        force_tier = Tier.TIER_2

    results: list[CheckResult] = []

    # 1. Audit (gh API checks)
    if not args.skip_audit:
        try:
            results.extend(run_audit(repo, force_tier=force_tier))
        except GhError as e:
            results.append(CheckResult(
                "Audit", "audit_invocation", "FAIL", f"{e}",
            ))

    # 2. Wiring checks (local file reads)
    results.append(check_precommit_has_verify_readme_sync(repo_root))
    results.append(check_cd_has_verify_readme_sync_job(repo_root))
    results.append(check_codeowners_has_admin(repo_root))
    results.append(check_ci_uses_repo_bootstrap_verify(repo_root))

    output = render_results(results, args.format)
    if args.output_file:
        Path(args.output_file).write_text(output, encoding="utf-8")
    else:
        print(output)

    if args.counts_file:
        write_counts_file(results, args.counts_file)

    return 1 if has_failure(results) else 0


if __name__ == "__main__":
    sys.exit(main())
