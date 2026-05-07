#!/usr/bin/env python3
"""6-medium GitHub-detail audit for n24q02m repo standards.

Usage:
    python audit.py --repo=n24q02m/skret --format=table
    python audit.py --repo=n24q02m/skret --format=json --output-file=out.json
    python audit.py --tier=1 --repo=n24q02m/some-new-repo

Returns exit 0 if all checks PASS or SKIP; exit 1 if any FAIL.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running directly OR as module
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import (  # type: ignore[import-not-found]
    AuditContext,
    CheckResult,
    GhError,
    Tier,
    build_audit_context,
    check,
    get_registry,
    has_failure,
    normalize_for_match,
    extract_readme_tagline,
    render_results,
    write_counts_file,
)

# ---------------------------------------------------------------------------
# Constants — required root files per tier
# ---------------------------------------------------------------------------

TIER_1_PUBLIC_ROOT_FILES = [
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "renovate.json",
    ".mise.toml",
    ".pre-commit-config.yaml",
    ".pr_agent.toml",
    ".skret.yaml",
]

TIER_2_PUBLIC_ROOT_FILES = [
    "LICENSE",
    "README.md",
    "renovate.json",
]

TIER_1_GITHUB_FILES = [
    ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/best_practices.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/rulesets/main.json",
    ".github/workflows/ci.yml",
    ".github/workflows/cd.yml",
]

STANDARD_LABELS = {"bug", "enhancement", "dependencies", "documentation", "security"}


# ---------------------------------------------------------------------------
# Helper — read repo file via gh API (works without local clone)
# ---------------------------------------------------------------------------


def _gh_file_exists(ctx: AuditContext, path: str) -> bool:
    """Check if a file exists in the repo's default branch via gh API."""
    try:
        ctx.gh.api(f"repos/{ctx.repo}/contents/{path}")
        return True
    except GhError as e:
        if "404" in str(e) or "Not Found" in str(e):
            return False
        raise


def _gh_file_content(ctx: AuditContext, path: str) -> str | None:
    """Fetch file content as decoded UTF-8 string. Returns None if not found."""
    try:
        data = ctx.gh.api(f"repos/{ctx.repo}/contents/{path}")
    except GhError:
        return None
    import base64

    if not isinstance(data, dict) or "content" not in data:
        return None
    try:
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return None


# ===========================================================================
# About panel checks (4)
# ===========================================================================


@check(group="About panel", name="description_present_and_size")
def check_description(ctx: AuditContext) -> CheckResult:
    info = ctx.gh.repo_view(ctx.repo, ["description"])
    desc = (info.get("description") or "").strip()
    if not desc:
        return CheckResult(
            "About panel", "description_present_and_size", "FAIL",
            "Repo description is empty",
            evidence={"description": desc},
        )
    if len(desc) > 350:
        return CheckResult(
            "About panel", "description_present_and_size", "FAIL",
            f"Description exceeds 350 chars ({len(desc)})",
            evidence={"length": len(desc)},
        )
    return CheckResult(
        "About panel", "description_present_and_size", "PASS",
        f"Description set ({len(desc)} chars)",
    )


@check(group="About panel", name="description_matches_readme_tagline")
def check_description_matches_tagline(ctx: AuditContext) -> CheckResult:
    info = ctx.gh.repo_view(ctx.repo, ["description"])
    desc = (info.get("description") or "").strip()
    readme = _gh_file_content(ctx, "README.md")
    if not readme:
        return CheckResult(
            "About panel", "description_matches_readme_tagline", "SKIP",
            "README.md not found — covered by other check",
        )
    tagline = extract_readme_tagline(readme)
    if not tagline:
        return CheckResult(
            "About panel", "description_matches_readme_tagline", "SKIP",
            "Could not extract tagline from README",
        )
    if normalize_for_match(desc) == normalize_for_match(tagline):
        return CheckResult(
            "About panel", "description_matches_readme_tagline", "PASS",
            "Description matches README tagline",
        )
    return CheckResult(
        "About panel", "description_matches_readme_tagline", "FAIL",
        "Description != README tagline (line 3)",
        evidence={"description": desc, "tagline": tagline},
    )


@check(group="About panel", name="homepage_set")
def check_homepage(ctx: AuditContext) -> CheckResult:
    info = ctx.gh.repo_view(ctx.repo, ["homepageUrl"])
    url = (info.get("homepageUrl") or "").strip()
    if ctx.tier is Tier.TIER_1:
        if not url:
            return CheckResult(
                "About panel", "homepage_set", "FAIL",
                "Tier 1 repo missing homepage URL",
            )
        if not (".n24q02m.com" in url or url.startswith("https://github.com/n24q02m/")):
            return CheckResult(
                "About panel", "homepage_set", "FAIL",
                f"Homepage should point to n24q02m.com or github (got {url})",
                evidence={"homepage": url},
            )
        return CheckResult("About panel", "homepage_set", "PASS", url)
    return CheckResult(
        "About panel", "homepage_set", "SKIP",
        "Tier 2 — homepage optional",
    )


@check(group="About panel", name="topics_minimum_three")
def check_topics(ctx: AuditContext) -> CheckResult:
    if len(ctx.topics) >= 3:
        return CheckResult(
            "About panel", "topics_minimum_three", "PASS",
            f"{len(ctx.topics)} topics: {', '.join(ctx.topics[:5])}",
        )
    return CheckResult(
        "About panel", "topics_minimum_three", "FAIL",
        f"Only {len(ctx.topics)} topics (need >=3)",
        evidence={"topics": ctx.topics},
    )


# ===========================================================================
# General settings (3)
# ===========================================================================


@check(group="General", name="default_branch_main")
def check_default_branch(ctx: AuditContext) -> CheckResult:
    info = ctx.gh.repo_view(ctx.repo, ["defaultBranchRef"])
    branch = (info.get("defaultBranchRef") or {}).get("name", "")
    if branch == "main":
        return CheckResult("General", "default_branch_main", "PASS", "main")
    return CheckResult(
        "General", "default_branch_main", "FAIL",
        f"Default branch is '{branch}', not 'main'",
        evidence={"branch": branch},
    )


@check(group="General", name="merge_method_squash_only")
def check_merge_squash_only(ctx: AuditContext) -> CheckResult:
    info = ctx.gh.repo_view(
        ctx.repo, ["mergeCommitAllowed", "rebaseMergeAllowed", "squashMergeAllowed"]
    )
    squash = info.get("squashMergeAllowed", False)
    merge = info.get("mergeCommitAllowed", True)
    rebase = info.get("rebaseMergeAllowed", True)
    if squash and not merge and not rebase:
        return CheckResult("General", "merge_method_squash_only", "PASS", "Squash only")
    return CheckResult(
        "General", "merge_method_squash_only", "FAIL",
        f"Allowed: squash={squash} merge={merge} rebase={rebase}",
        evidence={"squash": squash, "merge": merge, "rebase": rebase},
    )


@check(group="General", name="not_archived")
def check_not_archived(ctx: AuditContext) -> CheckResult:
    if ctx.is_archived:
        return CheckResult(
            "General", "not_archived", "FAIL",
            "Repo is archived (Spec G targets active repos only)",
        )
    return CheckResult("General", "not_archived", "PASS", "Active repo")


# ===========================================================================
# Branches/Rulesets (2)
# ===========================================================================


@check(group="Branches", name="main_ruleset_applied")
def check_main_ruleset(ctx: AuditContext) -> CheckResult:
    try:
        rulesets = ctx.gh.api(f"repos/{ctx.repo}/rulesets")
    except GhError as e:
        return CheckResult(
            "Branches", "main_ruleset_applied", "FAIL",
            f"Could not list rulesets: {e}",
        )
    if not isinstance(rulesets, list):
        return CheckResult(
            "Branches", "main_ruleset_applied", "FAIL",
            f"Unexpected rulesets response type: {type(rulesets).__name__}",
        )
    main_rulesets = [r for r in rulesets if r.get("target") == "branch" and r.get("enforcement") == "active"]
    if main_rulesets:
        return CheckResult(
            "Branches", "main_ruleset_applied", "PASS",
            f"{len(main_rulesets)} active branch ruleset(s)",
        )
    return CheckResult(
        "Branches", "main_ruleset_applied", "FAIL",
        "No active branch rulesets found",
    )


@check(group="Branches", name="ruleset_bypass_admin_only")
def check_ruleset_bypass(ctx: AuditContext) -> CheckResult:
    try:
        rulesets = ctx.gh.api(f"repos/{ctx.repo}/rulesets")
    except GhError:
        return CheckResult(
            "Branches", "ruleset_bypass_admin_only", "SKIP",
            "Could not query rulesets — depends on main_ruleset_applied",
        )
    if not isinstance(rulesets, list):
        return CheckResult("Branches", "ruleset_bypass_admin_only", "SKIP", "No rulesets")

    # bypass_actors filter: only repo admin (role) allowed
    suspicious: list[str] = []
    for rs in rulesets:
        actors = rs.get("bypass_actors") or []
        for a in actors:
            actor_type = a.get("actor_type") or ""
            if actor_type and actor_type not in {"RepositoryRole", "Team"}:
                suspicious.append(f"{rs.get('name')}: {actor_type}")
    if suspicious:
        return CheckResult(
            "Branches", "ruleset_bypass_admin_only", "FAIL",
            f"Non-admin bypass actors: {', '.join(suspicious)}",
            evidence={"actors": suspicious},
        )
    return CheckResult(
        "Branches", "ruleset_bypass_admin_only", "PASS",
        "Bypass restricted to admin/teams",
    )


# ===========================================================================
# Code security (5)
# ===========================================================================


@check(group="Code security", name="codeql_or_semgrep_configured")
def check_code_scanning(ctx: AuditContext) -> CheckResult:
    if ctx.is_public:
        # Look for CodeQL workflow or codeql-config in .github/workflows/
        if _gh_file_exists(ctx, ".github/workflows/codeql.yml") or _gh_file_exists(
            ctx, ".github/workflows/codeql-analysis.yml"
        ):
            return CheckResult(
                "Code security", "codeql_or_semgrep_configured", "PASS",
                "CodeQL workflow present",
            )
        # Some repos enable CodeQL via "default setup" with no workflow file —
        # check via API analyses endpoint (best-effort).
        try:
            analyses = ctx.gh.api(f"repos/{ctx.repo}/code-scanning/analyses?per_page=1")
            if isinstance(analyses, list) and len(analyses) > 0:
                return CheckResult(
                    "Code security", "codeql_or_semgrep_configured", "PASS",
                    "CodeQL default-setup active (analyses present)",
                )
        except GhError:
            pass
        return CheckResult(
            "Code security", "codeql_or_semgrep_configured", "FAIL",
            "Public repo missing CodeQL setup",
        )
    # Private — check for Semgrep
    if _gh_file_exists(ctx, ".github/workflows/semgrep.yml"):
        return CheckResult(
            "Code security", "codeql_or_semgrep_configured", "PASS",
            "Semgrep workflow present",
        )
    return CheckResult(
        "Code security", "codeql_or_semgrep_configured", "FAIL",
        "Private repo missing Semgrep workflow",
    )


def _get_security_and_analysis(ctx: AuditContext) -> dict:
    """Fetch security_and_analysis block via direct REST API (gh repo view doesn't expose it)."""
    full = ctx.gh.api(f"repos/{ctx.repo}")
    if isinstance(full, dict):
        return full.get("security_and_analysis") or {}
    return {}


@check(group="Code security", name="secret_scanning_enabled")
def check_secret_scanning(ctx: AuditContext) -> CheckResult:
    sa = _get_security_and_analysis(ctx)
    state = (sa.get("secret_scanning") or {}).get("status", "")
    if state == "enabled":
        return CheckResult("Code security", "secret_scanning_enabled", "PASS", state)
    return CheckResult(
        "Code security", "secret_scanning_enabled", "FAIL",
        f"Secret scanning status: {state or 'unknown'}",
        evidence={"security_and_analysis": sa},
    )


@check(group="Code security", name="push_protection_enabled")
def check_push_protection(ctx: AuditContext) -> CheckResult:
    sa = _get_security_and_analysis(ctx)
    state = (sa.get("secret_scanning_push_protection") or {}).get("status", "")
    if state == "enabled":
        return CheckResult("Code security", "push_protection_enabled", "PASS", state)
    return CheckResult(
        "Code security", "push_protection_enabled", "FAIL",
        f"Push protection status: {state or 'unknown'}",
    )


@check(group="Code security", name="private_vulnerability_reporting")
def check_private_vuln_reporting(ctx: AuditContext) -> CheckResult:
    try:
        info = ctx.gh.api(f"repos/{ctx.repo}/private-vulnerability-reporting")
    except GhError as e:
        return CheckResult(
            "Code security", "private_vulnerability_reporting", "SKIP",
            f"API error: {e}",
        )
    enabled = info.get("enabled") if isinstance(info, dict) else False
    if enabled:
        return CheckResult(
            "Code security", "private_vulnerability_reporting", "PASS",
            "enabled",
        )
    return CheckResult(
        "Code security", "private_vulnerability_reporting", "FAIL",
        "Private vulnerability reporting disabled",
    )


@check(group="Code security", name="dependabot_alerts_enabled")
def check_dependabot(ctx: AuditContext) -> CheckResult:
    sa = _get_security_and_analysis(ctx)
    dep = (sa.get("dependabot_security_updates") or {}).get("status", "")
    if dep == "enabled":
        return CheckResult("Code security", "dependabot_alerts_enabled", "PASS", dep)
    info = ctx.gh.repo_view(ctx.repo, ["hasVulnerabilityAlertsEnabled"])
    if info.get("hasVulnerabilityAlertsEnabled") is True:
        return CheckResult(
            "Code security", "dependabot_alerts_enabled", "PASS",
            "hasVulnerabilityAlertsEnabled=true",
        )
    return CheckResult(
        "Code security", "dependabot_alerts_enabled", "FAIL",
        f"Dependabot alerts not detected (status={dep or 'unknown'})",
    )


# ===========================================================================
# Webhooks (3)
# ===========================================================================


def _has_hook_with_url(ctx: AuditContext, url_substring: str) -> bool:
    try:
        hooks = ctx.gh.api(f"repos/{ctx.repo}/hooks")
    except GhError:
        return False
    if not isinstance(hooks, list):
        return False
    for h in hooks:
        config = h.get("config") or {}
        if url_substring in (config.get("url") or ""):
            return True
    return False


@check(group="Webhooks", name="renovate_app_installed")
def check_renovate(ctx: AuditContext) -> CheckResult:
    # Renovate runs as GitHub App; presence detected via renovate.json existing
    # AND most recent issue from `renovate[bot]` author OR app-level installation list (admin-only)
    if _gh_file_exists(ctx, "renovate.json") or _gh_file_exists(ctx, ".github/renovate.json"):
        return CheckResult(
            "Webhooks", "renovate_app_installed", "PASS",
            "renovate.json config present",
        )
    return CheckResult(
        "Webhooks", "renovate_app_installed", "FAIL",
        "No renovate.json found",
    )


@check(group="Webhooks", name="codecov_app_installed")
def check_codecov(ctx: AuditContext) -> CheckResult:
    if ctx.tier is not Tier.TIER_1:
        return CheckResult("Webhooks", "codecov_app_installed", "SKIP", "Tier 2 — Codecov optional")
    # Detect Codecov badge in README OR codecov.yml config
    if _gh_file_exists(ctx, "codecov.yml") or _gh_file_exists(ctx, ".codecov.yml"):
        return CheckResult("Webhooks", "codecov_app_installed", "PASS", "codecov config present")
    readme = _gh_file_content(ctx, "README.md") or ""
    if "codecov.io" in readme:
        return CheckResult("Webhooks", "codecov_app_installed", "PASS", "Codecov badge in README")
    return CheckResult(
        "Webhooks", "codecov_app_installed", "FAIL",
        "No Codecov config or badge found",
    )


@check(group="Webhooks", name="cloudflare_pages_claim")
def check_cf_pages(ctx: AuditContext) -> CheckResult:
    if not ctx.is_docs_site:
        return CheckResult("Webhooks", "cloudflare_pages_claim", "SKIP", "Not a docs-site repo")
    # Best-effort: look for wrangler config or pages-deploy workflow
    if _gh_file_exists(ctx, "wrangler.toml") or _gh_file_exists(ctx, ".github/workflows/pages.yml"):
        return CheckResult(
            "Webhooks", "cloudflare_pages_claim", "PASS",
            "Pages deploy config present",
        )
    return CheckResult(
        "Webhooks", "cloudflare_pages_claim", "FAIL",
        "Docs-site repo missing Cloudflare Pages config",
    )


# ===========================================================================
# Issues/PRs (6)
# ===========================================================================


def _check_github_file(ctx: AuditContext, path: str, group: str, name: str) -> CheckResult:
    if _gh_file_exists(ctx, path):
        return CheckResult(group, name, "PASS", path)
    return CheckResult(group, name, "FAIL", f"Missing {path}")


@check(group="Issues/PRs", name="codeowners_present")
def check_codeowners(ctx: AuditContext) -> CheckResult:
    return _check_github_file(ctx, ".github/CODEOWNERS", "Issues/PRs", "codeowners_present")


@check(group="Issues/PRs", name="pr_template_present")
def check_pr_template(ctx: AuditContext) -> CheckResult:
    return _check_github_file(
        ctx, ".github/PULL_REQUEST_TEMPLATE.md", "Issues/PRs", "pr_template_present"
    )


@check(group="Issues/PRs", name="bug_report_template_present")
def check_bug_template(ctx: AuditContext) -> CheckResult:
    return _check_github_file(
        ctx, ".github/ISSUE_TEMPLATE/bug_report.md", "Issues/PRs", "bug_report_template_present"
    )


@check(group="Issues/PRs", name="feature_request_template_present")
def check_feature_template(ctx: AuditContext) -> CheckResult:
    return _check_github_file(
        ctx, ".github/ISSUE_TEMPLATE/feature_request.md",
        "Issues/PRs", "feature_request_template_present",
    )


@check(group="Issues/PRs", name="best_practices_present")
def check_best_practices(ctx: AuditContext) -> CheckResult:
    if ctx.tier is not Tier.TIER_1:
        return CheckResult("Issues/PRs", "best_practices_present", "SKIP", "Tier 2 — optional")
    return _check_github_file(
        ctx, ".github/best_practices.md", "Issues/PRs", "best_practices_present"
    )


@check(group="Issues/PRs", name="standard_labels_present")
def check_labels(ctx: AuditContext) -> CheckResult:
    try:
        labels = ctx.gh.api(f"repos/{ctx.repo}/labels?per_page=100")
    except GhError as e:
        return CheckResult("Issues/PRs", "standard_labels_present", "FAIL", f"API error: {e}")
    if not isinstance(labels, list):
        return CheckResult("Issues/PRs", "standard_labels_present", "FAIL", "Unexpected response")
    names = {(l.get("name") or "").lower() for l in labels}
    missing = STANDARD_LABELS - names
    if missing:
        return CheckResult(
            "Issues/PRs", "standard_labels_present", "FAIL",
            f"Missing labels: {', '.join(sorted(missing))}",
            evidence={"missing": sorted(missing), "found_count": len(names)},
        )
    return CheckResult(
        "Issues/PRs", "standard_labels_present", "PASS",
        f"All 5 standard labels present",
    )


# ===========================================================================
# Discussions (1)
# ===========================================================================


@check(group="Discussions", name="discussions_enabled")
def check_discussions(ctx: AuditContext) -> CheckResult:
    if not (ctx.tier is Tier.TIER_1 and ctx.is_public):
        return CheckResult(
            "Discussions", "discussions_enabled", "SKIP",
            "Tier 2 or private — Discussions optional",
        )
    info = ctx.gh.repo_view(ctx.repo, ["hasDiscussionsEnabled"])
    if info.get("hasDiscussionsEnabled"):
        return CheckResult("Discussions", "discussions_enabled", "PASS", "enabled")
    return CheckResult(
        "Discussions", "discussions_enabled", "FAIL",
        "Tier 1 public repo should have Discussions enabled",
    )


# ===========================================================================
# Community Standards (1)
# ===========================================================================


@check(group="Community Standards", name="community_profile_complete")
def check_community(ctx: AuditContext) -> CheckResult:
    try:
        profile = ctx.gh.api(f"repos/{ctx.repo}/community/profile")
    except GhError as e:
        return CheckResult(
            "Community Standards", "community_profile_complete", "SKIP",
            f"API error: {e}",
        )
    if not isinstance(profile, dict):
        return CheckResult(
            "Community Standards", "community_profile_complete", "SKIP",
            "Unexpected response",
        )
    health = profile.get("health_percentage", 0)
    if health == 100:
        return CheckResult(
            "Community Standards", "community_profile_complete", "PASS",
            "Health 100%",
        )
    files = profile.get("files") or {}
    required = ("readme", "license", "code_of_conduct", "contributing", "pull_request_template")
    missing = [k for k in required if not (files.get(k) or {})]
    return CheckResult(
        "Community Standards", "community_profile_complete", "FAIL",
        f"Health {health}%, missing: {', '.join(missing) or 'none'}",
        evidence={"health": health, "missing": missing},
    )


# ===========================================================================
# Root files (tier-aware) (1 check that loops)
# ===========================================================================


@check(group="Root files", name="required_root_files_present")
def check_root_files(ctx: AuditContext) -> CheckResult:
    if ctx.tier is Tier.TIER_1 and ctx.is_public:
        required = TIER_1_PUBLIC_ROOT_FILES
    else:
        required = TIER_2_PUBLIC_ROOT_FILES
    missing: list[str] = []
    for f in required:
        if not _gh_file_exists(ctx, f):
            missing.append(f)
    if missing:
        return CheckResult(
            "Root files", "required_root_files_present", "FAIL",
            f"Missing: {', '.join(missing)}",
            evidence={"missing": missing, "tier": ctx.tier.name},
        )
    return CheckResult(
        "Root files", "required_root_files_present", "PASS",
        f"All {len(required)} required root files present",
    )


@check(group="Root files", name="github_files_present")
def check_github_files(ctx: AuditContext) -> CheckResult:
    if ctx.tier is not Tier.TIER_1:
        return CheckResult(
            "Root files", "github_files_present", "SKIP",
            "Tier 2 — .github files optional",
        )
    missing = [f for f in TIER_1_GITHUB_FILES if not _gh_file_exists(ctx, f)]
    if missing:
        return CheckResult(
            "Root files", "github_files_present", "FAIL",
            f"Missing: {', '.join(missing)}",
            evidence={"missing": missing},
        )
    return CheckResult(
        "Root files", "github_files_present", "PASS",
        f"All {len(TIER_1_GITHUB_FILES)} .github files present",
    )


# ===========================================================================
# README compliance (5)
# ===========================================================================


@check(group="README", name="readme_has_tagline")
def check_readme_tagline(ctx: AuditContext) -> CheckResult:
    readme = _gh_file_content(ctx, "README.md")
    if not readme:
        return CheckResult("README", "readme_has_tagline", "FAIL", "README.md not found")
    tagline = extract_readme_tagline(readme)
    if tagline and len(tagline) >= 10:
        return CheckResult(
            "README", "readme_has_tagline", "PASS",
            f"Tagline: {tagline[:50]}...",
        )
    return CheckResult(
        "README", "readme_has_tagline", "FAIL",
        "No substantive tagline found in README",
    )


@check(group="README", name="readme_has_two_badge_rows")
def check_badge_rows(ctx: AuditContext) -> CheckResult:
    readme = _gh_file_content(ctx, "README.md")
    if not readme:
        return CheckResult("README", "readme_has_two_badge_rows", "SKIP", "README missing")
    # Heuristic: count distinct lines/blocks containing badge images
    import re

    badge_lines = [ln for ln in readme.splitlines() if re.search(r"\[!\[[^\]]+\]\([^\)]+\)\]\([^\)]+\)", ln)]
    if len(badge_lines) >= 2 or readme.count("img.shields.io") >= 4:
        return CheckResult(
            "README", "readme_has_two_badge_rows", "PASS",
            f"{readme.count('img.shields.io')} shield badges found",
        )
    return CheckResult(
        "README", "readme_has_two_badge_rows", "FAIL",
        "Less than 2 badge rows / 4 shield badges detected",
    )


@check(group="README", name="readme_has_cross_promo_block")
def check_cross_promo(ctx: AuditContext) -> CheckResult:
    if ctx.tier is not Tier.TIER_1:
        return CheckResult(
            "README", "readme_has_cross_promo_block", "SKIP",
            "Tier 2 — cross-promo optional",
        )
    readme = _gh_file_content(ctx, "README.md") or ""
    if "AUTO-GENERATED-CROSS-PROMO" in readme:
        return CheckResult(
            "README", "readme_has_cross_promo_block", "PASS",
            "Cross-promo block delimiters present",
        )
    return CheckResult(
        "README", "readme_has_cross_promo_block", "FAIL",
        "No <!-- BEGIN/END: AUTO-GENERATED-CROSS-PROMO --> delimiters found",
    )


@check(group="README", name="readme_has_table_of_contents")
def check_toc(ctx: AuditContext) -> CheckResult:
    if ctx.tier is not Tier.TIER_1:
        return CheckResult("README", "readme_has_table_of_contents", "SKIP", "Tier 2 optional")
    readme = _gh_file_content(ctx, "README.md") or ""
    if "## Table of contents" in readme or "## Table of Contents" in readme:
        return CheckResult("README", "readme_has_table_of_contents", "PASS", "TOC heading found")
    return CheckResult(
        "README", "readme_has_table_of_contents", "FAIL",
        "No '## Table of contents' heading",
    )


@check(group="README", name="readme_has_install_matrix")
def check_install_matrix(ctx: AuditContext) -> CheckResult:
    if ctx.tier is not Tier.TIER_1:
        return CheckResult("README", "readme_has_install_matrix", "SKIP", "Tier 2 — install single-snippet")
    readme = _gh_file_content(ctx, "README.md") or ""
    if "## Install" in readme and "| Platform" in readme:
        return CheckResult("README", "readme_has_install_matrix", "PASS", "Install matrix table found")
    return CheckResult(
        "README", "readme_has_install_matrix", "FAIL",
        "No '## Install' section with Platform table",
    )


# ===========================================================================
# Main
# ===========================================================================


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="6-medium GitHub-detail audit")
    p.add_argument("--repo", required=True, help="owner/name (e.g. n24q02m/skret)")
    p.add_argument("--format", default="table", choices=["json", "table", "markdown"])
    p.add_argument("--tier", choices=["1", "2"], help="Force tier (auto-detect from Stars list otherwise)")
    p.add_argument("--output-file", help="Write formatted output to this file (default: stdout)")
    p.add_argument("--counts-file", help="Write counts JSON to this file (used by composite actions)")
    return p.parse_args()


def run_audit(repo: str, force_tier: Tier | None = None) -> list[CheckResult]:
    ctx = build_audit_context(repo, force_tier=force_tier)
    results: list[CheckResult] = []
    for group, name, fn in get_registry():
        try:
            r = fn(ctx)
        except GhError as e:
            r = CheckResult(group, name, "FAIL", f"GhError: {e}")
        except Exception as e:
            r = CheckResult(group, name, "FAIL", f"Internal error: {type(e).__name__}: {e}")
        results.append(r)
    return results


def main() -> int:
    # Force UTF-8 stdout/stderr (Windows cp1252 default chokes on Unicode)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    force_tier = None
    if args.tier == "1":
        force_tier = Tier.TIER_1
    elif args.tier == "2":
        force_tier = Tier.TIER_2
    results = run_audit(args.repo, force_tier=force_tier)
    output = render_results(results, args.format)
    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)
    if args.counts_file:
        write_counts_file(results, args.counts_file)
    return 1 if has_failure(results) else 0


if __name__ == "__main__":
    sys.exit(main())
