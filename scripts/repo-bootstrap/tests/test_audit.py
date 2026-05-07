"""Unit tests for audit.py — mock gh responses + verify check function logic.

Run from repo root:
    python -m pytest scripts/repo-bootstrap/tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts/repo-bootstrap/ to path so audit + _lib import correctly
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

import audit  # type: ignore[import-not-found]
from _lib import AuditContext, GhClient, Tier  # type: ignore[import-not-found]


def make_ctx(
    *,
    repo: str = "n24q02m/test-repo",
    tier: Tier = Tier.TIER_1,
    is_public: bool = True,
    primary_lang: str = "Python",
    topics: list[str] | None = None,
    is_archived: bool = False,
    is_docs_site: bool = False,
) -> AuditContext:
    return AuditContext(
        repo=repo,
        tier=tier,
        is_public=is_public,
        is_archived=is_archived,
        primary_language=primary_lang,
        topics=topics or ["python", "mcp", "ai"],
        is_docs_site=is_docs_site,
        gh=GhClient(),
    )


# ---------------------------------------------------------------------------
# About panel
# ---------------------------------------------------------------------------


def test_check_description_pass():
    ctx = make_ctx()
    with patch.object(GhClient, "repo_view", return_value={"description": "A normal tagline"}):
        result = audit.check_description(ctx)
    assert result.status == "PASS"


def test_check_description_empty_fails():
    ctx = make_ctx()
    with patch.object(GhClient, "repo_view", return_value={"description": ""}):
        result = audit.check_description(ctx)
    assert result.status == "FAIL"
    assert "empty" in result.message.lower()


def test_check_description_too_long_fails():
    ctx = make_ctx()
    with patch.object(GhClient, "repo_view", return_value={"description": "x" * 351}):
        result = audit.check_description(ctx)
    assert result.status == "FAIL"


def test_check_topics_pass():
    ctx = make_ctx(topics=["python", "ai", "mcp", "cli"])
    result = audit.check_topics(ctx)
    assert result.status == "PASS"


def test_check_topics_too_few_fails():
    ctx = make_ctx(topics=["python"])
    result = audit.check_topics(ctx)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# General settings
# ---------------------------------------------------------------------------


def test_check_default_branch_main_pass():
    ctx = make_ctx()
    with patch.object(
        GhClient, "repo_view",
        return_value={"defaultBranchRef": {"name": "main"}},
    ):
        result = audit.check_default_branch(ctx)
    assert result.status == "PASS"


def test_check_default_branch_master_fails():
    ctx = make_ctx()
    with patch.object(
        GhClient, "repo_view",
        return_value={"defaultBranchRef": {"name": "master"}},
    ):
        result = audit.check_default_branch(ctx)
    assert result.status == "FAIL"


def test_check_squash_only_pass():
    ctx = make_ctx()
    with patch.object(
        GhClient, "repo_view",
        return_value={
            "squashMergeAllowed": True,
            "mergeCommitAllowed": False,
            "rebaseMergeAllowed": False,
        },
    ):
        result = audit.check_merge_squash_only(ctx)
    assert result.status == "PASS"


def test_check_squash_only_with_merge_fails():
    ctx = make_ctx()
    with patch.object(
        GhClient, "repo_view",
        return_value={
            "squashMergeAllowed": True,
            "mergeCommitAllowed": True,
            "rebaseMergeAllowed": False,
        },
    ):
        result = audit.check_merge_squash_only(ctx)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# Code security
# ---------------------------------------------------------------------------


def test_check_secret_scanning_enabled():
    ctx = make_ctx()
    with patch.object(
        GhClient, "repo_view",
        return_value={"securityAndAnalysis": {"secret_scanning": {"status": "enabled"}}},
    ):
        result = audit.check_secret_scanning(ctx)
    assert result.status == "PASS"


def test_check_secret_scanning_disabled():
    ctx = make_ctx()
    with patch.object(
        GhClient, "repo_view",
        return_value={"securityAndAnalysis": {"secret_scanning": {"status": "disabled"}}},
    ):
        result = audit.check_secret_scanning(ctx)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# Issues/PRs labels
# ---------------------------------------------------------------------------


def test_check_labels_all_present():
    ctx = make_ctx()
    labels_response = [
        {"name": "bug"},
        {"name": "enhancement"},
        {"name": "dependencies"},
        {"name": "documentation"},
        {"name": "security"},
    ]
    with patch.object(GhClient, "api", return_value=labels_response):
        result = audit.check_labels(ctx)
    assert result.status == "PASS"


def test_check_labels_missing_some():
    ctx = make_ctx()
    labels_response = [{"name": "bug"}, {"name": "enhancement"}]
    with patch.object(GhClient, "api", return_value=labels_response):
        result = audit.check_labels(ctx)
    assert result.status == "FAIL"
    assert "dependencies" in result.message
    assert "documentation" in result.message
    assert "security" in result.message


# ---------------------------------------------------------------------------
# README compliance
# ---------------------------------------------------------------------------


def test_check_readme_tagline_pass():
    ctx = make_ctx()
    readme_text = """<p align="center">
  <img src="logo.svg" width="120">
</p>

<h1 align="center">my-tool</h1>

<p align="center">
  <strong>This is the substantive tagline that describes my-tool.</strong>
</p>
"""
    with patch.object(audit, "_gh_file_content", return_value=readme_text):
        result = audit.check_readme_tagline(ctx)
    assert result.status == "PASS"


def test_check_readme_tagline_no_readme():
    ctx = make_ctx()
    with patch.object(audit, "_gh_file_content", return_value=None):
        result = audit.check_readme_tagline(ctx)
    assert result.status == "FAIL"


def test_check_cross_promo_block_present():
    ctx = make_ctx()
    readme_text = "...\n<!-- BEGIN: AUTO-GENERATED-CROSS-PROMO -->\nstuff\n<!-- END: AUTO-GENERATED-CROSS-PROMO -->\n"
    with patch.object(audit, "_gh_file_content", return_value=readme_text):
        result = audit.check_cross_promo(ctx)
    assert result.status == "PASS"


def test_check_cross_promo_tier_2_skipped():
    ctx = make_ctx(tier=Tier.TIER_2)
    result = audit.check_cross_promo(ctx)
    assert result.status == "SKIP"
