"""Unit tests for verify_readme_sync.py — uses tmp directories with manifest fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

import verify_readme_sync as vrs  # type: ignore[import-not-found]


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    """Empty tmp dir representing a repo root."""
    return tmp_path


# ---------------------------------------------------------------------------
# Universal: README + tagline
# ---------------------------------------------------------------------------


def test_readme_exists_pass(repo_root: Path):
    (repo_root / "README.md").write_text("# Title\n\nA tagline that describes the tool.\n", encoding="utf-8")
    result = vrs.check_readme_exists(repo_root)
    assert result.status == "PASS"


def test_readme_missing_fail(repo_root: Path):
    result = vrs.check_readme_exists(repo_root)
    assert result.status == "FAIL"


def test_readme_tagline_present(repo_root: Path):
    (repo_root / "README.md").write_text(
        "<h1 align=\"center\">tool</h1>\n\n"
        "<p align=\"center\"><strong>A precise concise tagline for the tool.</strong></p>\n",
        encoding="utf-8",
    )
    result = vrs.check_readme_tagline(repo_root)
    assert result.status == "PASS"


def test_readme_tagline_too_short(repo_root: Path):
    (repo_root / "README.md").write_text("# tool\n\nshort\n", encoding="utf-8")
    result = vrs.check_readme_tagline(repo_root)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# Python — pyproject.toml
# ---------------------------------------------------------------------------


def test_python_readme_field_pass(repo_root: Path):
    (repo_root / "pyproject.toml").write_text(
        '[project]\nname = "x"\nreadme = "README.md"\n', encoding="utf-8"
    )
    result = vrs.check_python_readme_field(repo_root)
    assert result.status == "PASS"


def test_python_readme_field_missing_fail(repo_root: Path):
    (repo_root / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    result = vrs.check_python_readme_field(repo_root)
    assert result.status == "FAIL"


def test_python_readme_field_skip_no_pyproject(repo_root: Path):
    result = vrs.check_python_readme_field(repo_root)
    assert result.status == "SKIP"


# ---------------------------------------------------------------------------
# TypeScript — package.json
# ---------------------------------------------------------------------------


def test_ts_repository_field_pass(repo_root: Path):
    (repo_root / "package.json").write_text(
        json.dumps({
            "name": "x",
            "repository": {"type": "git", "url": "git+https://github.com/n24q02m/x.git"},
        }),
        encoding="utf-8",
    )
    result = vrs.check_ts_repository_field(repo_root)
    assert result.status == "PASS"


def test_ts_repository_field_string_form(repo_root: Path):
    (repo_root / "package.json").write_text(
        json.dumps({"name": "x", "repository": "git+https://github.com/n24q02m/x.git"}),
        encoding="utf-8",
    )
    result = vrs.check_ts_repository_field(repo_root)
    assert result.status == "PASS"


def test_ts_repository_field_wrong_org_fail(repo_root: Path):
    (repo_root / "package.json").write_text(
        json.dumps({"name": "x", "repository": "git+https://github.com/other-org/x.git"}),
        encoding="utf-8",
    )
    result = vrs.check_ts_repository_field(repo_root)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# Go/Docker — Dockerfile LABEL
# ---------------------------------------------------------------------------


def test_go_dockerfile_label_pass(repo_root: Path):
    (repo_root / "Dockerfile").write_text(
        'FROM golang:alpine\nLABEL org.opencontainers.image.source="https://github.com/n24q02m/skret"\n',
        encoding="utf-8",
    )
    result = vrs.check_go_dockerfile_ghcr_label(repo_root)
    assert result.status == "PASS"


def test_go_dockerfile_label_missing_fail(repo_root: Path):
    (repo_root / "Dockerfile").write_text("FROM golang:alpine\n", encoding="utf-8")
    result = vrs.check_go_dockerfile_ghcr_label(repo_root)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# MCP server description match
# ---------------------------------------------------------------------------


def test_mcp_description_match_pass(repo_root: Path):
    tagline = "A neat tool for X."
    (repo_root / "README.md").write_text(
        f"<h1>tool</h1>\n\n<p>{tagline}</p>\n", encoding="utf-8"
    )
    (repo_root / "server.json").write_text(
        json.dumps({"description": tagline}), encoding="utf-8"
    )
    result = vrs.check_mcp_server_description_matches(repo_root)
    assert result.status == "PASS"


def test_mcp_description_mismatch_fail(repo_root: Path):
    (repo_root / "README.md").write_text(
        "<h1>tool</h1>\n\n<p>The neat tool tagline that's substantive.</p>\n", encoding="utf-8"
    )
    (repo_root / "server.json").write_text(
        json.dumps({"description": "Some completely different description"}),
        encoding="utf-8",
    )
    result = vrs.check_mcp_server_description_matches(repo_root)
    assert result.status == "FAIL"


def test_mcp_skip_no_server_json(repo_root: Path):
    (repo_root / "README.md").write_text("# tool\n\nTagline\n", encoding="utf-8")
    result = vrs.check_mcp_server_description_matches(repo_root)
    assert result.status == "SKIP"
