"""Unit tests for repo-bootstrap init.py + apply.py + _lib_templating.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

import _lib_templating as lib  # type: ignore[import-not-found]
import apply  # type: ignore[import-not-found]


# ---------------------------------------------------------------------------
# _lib_templating
# ---------------------------------------------------------------------------


def test_render_substitutes_vars():
    assert lib.render("hello {{name}}", {"name": "world"}) == "hello world"


def test_render_strict_unknown_raises():
    with pytest.raises(KeyError):
        lib.render("hello {{name}}", {})


def test_safe_render_unknown_unchanged():
    assert lib.safe_render("hello {{name}} {{other}}", {"name": "X"}) == "hello X {{other}}"


def test_render_multiple_substitutions():
    out = lib.render(
        "Repo: {{owner}}/{{repo_name}} v{{year}}",
        {"owner": "n24q02m", "repo_name": "foo", "year": "2026"},
    )
    assert out == "Repo: n24q02m/foo v2026"


def test_text_hash_stable():
    h1 = lib.text_hash("abc")
    h2 = lib.text_hash("abc")
    assert h1 == h2
    assert h1 != lib.text_hash("abd")


def test_template_to_target_strips_tmpl(tmp_path: Path):
    template_root = tmp_path / "tmpl"
    template_root.mkdir()
    target_root = tmp_path / "target"
    src = template_root / "foo.md.tmpl"
    src.write_text("X")
    target = lib.template_to_target(src, template_root, target_root)
    assert target.name == "foo.md"
    assert target == target_root / "foo.md"


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------


def test_detect_language_python(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\n')
    assert lib.detect_language(tmp_path) == "python"


def test_detect_language_typescript(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"name": "x"}')
    assert lib.detect_language(tmp_path) == "typescript"


def test_detect_language_go(tmp_path: Path):
    (tmp_path / "go.mod").write_text("module github.com/x/y\n")
    assert lib.detect_language(tmp_path) == "go"


def test_detect_language_polyglot(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\n')
    (tmp_path / "package.json").write_text('{"name": "x"}')
    assert lib.detect_language(tmp_path) == "polyglot"


def test_detect_language_unknown(tmp_path: Path):
    assert lib.detect_language(tmp_path) == "unknown"


def test_is_psr_in_pyproject():
    assert lib.is_psr_in_pyproject("python") is True
    assert lib.is_psr_in_pyproject("typescript") is False
    assert lib.is_psr_in_pyproject("go") is False
    assert lib.is_psr_in_pyproject("rust") is False


# ---------------------------------------------------------------------------
# apply.py classify + deep_merge
# ---------------------------------------------------------------------------


def test_classify_skip_if_exists():
    assert apply.classify("AGENTS.md") == "skip-if-exists"
    assert apply.classify(".gitignore") == "skip-if-exists"
    assert apply.classify("README.md") == "skip-if-exists"


def test_classify_compose_only():
    assert apply.classify("renovate.json") == "compose-only"


def test_classify_atomic_replace():
    assert apply.classify("LICENSE") == "atomic-replace"
    assert apply.classify("CODE_OF_CONDUCT.md") == "atomic-replace"
    assert apply.classify("ci.yml") == "atomic-replace"


def test_deep_merge_preserves_user_keys():
    user = {"a": 1, "b": {"x": "user"}}
    template = {"b": {"y": "template"}, "c": 3}
    merged, conflicts = apply.deep_merge(user, template)
    assert merged == {"a": 1, "b": {"x": "user", "y": "template"}, "c": 3}
    assert conflicts == []


def test_deep_merge_conflict_keeps_user():
    user = {"a": "user_val"}
    template = {"a": "template_val"}
    merged, conflicts = apply.deep_merge(user, template)
    assert merged == {"a": "user_val"}
    assert len(conflicts) == 1
    assert "user_val" in conflicts[0]
    assert "template_val" in conflicts[0]


# ---------------------------------------------------------------------------
# render_and_write
# ---------------------------------------------------------------------------


def test_render_and_write_creates(tmp_path: Path):
    tpl = tmp_path / "src.tmpl"
    tpl.write_text("hello {{name}}")
    target = tmp_path / "out.txt"
    action = lib.render_and_write(tpl, target, {"name": "world"})
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "hello world"
    assert action.action in ("created", "replaced")


def test_render_and_write_skipped_if_identical(tmp_path: Path):
    tpl = tmp_path / "src.tmpl"
    tpl.write_text("hello {{name}}")
    target = tmp_path / "out.txt"
    target.write_text("hello world")
    action = lib.render_and_write(tpl, target, {"name": "world"})
    assert action.action == "skipped"


def test_render_and_write_dry_run(tmp_path: Path):
    tpl = tmp_path / "src.tmpl"
    tpl.write_text("hello {{name}}")
    target = tmp_path / "out.txt"
    action = lib.render_and_write(tpl, target, {"name": "world"}, dry_run=True)
    assert not target.exists()
    assert action.action in ("would-create", "would-replace")


# ---------------------------------------------------------------------------
# Replace managed region
# ---------------------------------------------------------------------------


def test_replace_managed_region_existing():
    text = """before
<!-- MANAGED-START: foo -->
old content
<!-- MANAGED-END: foo -->
after"""
    new, replaced = lib.replace_managed_region(text, "foo", "new content")
    assert replaced is True
    assert "new content" in new
    assert "old content" not in new
    assert "before" in new and "after" in new


def test_replace_managed_region_no_markers():
    text = "no markers here"
    new, replaced = lib.replace_managed_region(text, "foo", "x")
    assert replaced is False
    assert new == text
