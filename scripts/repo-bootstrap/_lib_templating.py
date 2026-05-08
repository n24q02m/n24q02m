"""Templating helpers for repo-bootstrap init.py + apply.py.

Pure stdlib. `{{var}}` syntax via simple `re.sub`.
Multiple file variants for conditionals (no Jinja2 dep).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_VAR_RE = re.compile(r"\{\{([_a-zA-Z][_a-zA-Z0-9]*)\}\}")


def render(template_text: str, variables: dict[str, Any]) -> str:
    """Render a template by substituting `{{var}}` with `variables[var]`.

    Unknown vars raise KeyError (strict mode). Use `safe_render` for lenient.
    """
    def replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        if var_name not in variables:
            raise KeyError(f"Template variable {{{{{var_name}}}}} not provided")
        return str(variables[var_name])

    return _VAR_RE.sub(replace, template_text)


def safe_render(template_text: str, variables: dict[str, Any]) -> str:
    """Render template, leaving unknown `{{vars}}` unchanged."""
    def replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        if var_name in variables:
            return str(variables[var_name])
        return match.group(0)  # leave unchanged

    return _VAR_RE.sub(replace, template_text)


def file_hash(path: Path) -> str:
    """SHA-256 hex digest of file content. Returns '' if file missing."""
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_hash(text: str) -> str:
    """SHA-256 hex digest of text bytes (UTF-8)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Managed-region helpers
# ---------------------------------------------------------------------------


_MANAGED_BEGIN_RE = re.compile(r"<!--\s*MANAGED-START:\s*(\S+)\s*-->")


def replace_managed_region(
    existing_text: str,
    region_key: str,
    new_content: str,
) -> tuple[str, bool]:
    """Replace content inside `<!-- MANAGED-START: <key> -->` / `<!-- MANAGED-END: <key> -->`.

    Returns (new_text, replaced). If markers absent, returns (existing_text, False).
    Caller decides whether to insert markers + content fresh.
    """
    pattern = re.compile(
        rf"(<!--\s*MANAGED-START:\s*{re.escape(region_key)}\s*-->).*?(<!--\s*MANAGED-END:\s*{re.escape(region_key)}\s*-->)",
        re.DOTALL,
    )
    new, n = pattern.subn(rf"\1\n{new_content}\n\2", existing_text, count=1)
    return new, n > 0


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class FileAction:
    """Single file operation outcome (used for dry-run + summary)."""

    path: Path
    action: str  # "created" | "skipped" | "replaced" | "merged" | "would-replace" | ...
    reason: str = ""
    diff_lines: int = 0


@dataclass
class ApplyReport:
    """Aggregate result of init / apply run."""

    actions: list[FileAction] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add(self, action: FileAction) -> None:
        self.actions.append(action)

    def summary(self) -> str:
        from collections import Counter

        counts = Counter(a.action for a in self.actions)
        return ", ".join(f"{n} {act}" for act, n in counts.items())


# ---------------------------------------------------------------------------
# Render + write helper
# ---------------------------------------------------------------------------


def render_and_write(
    template_path: Path,
    target_path: Path,
    variables: dict[str, Any],
    *,
    dry_run: bool = False,
    overwrite: bool = True,
) -> FileAction:
    """Render template + write to target. Strips `.tmpl` suffix from filename if present."""
    text = template_path.read_text(encoding="utf-8")
    rendered = safe_render(text, variables)

    if target_path.exists() and not overwrite:
        return FileAction(target_path, "skipped", reason="exists, no-overwrite")

    if target_path.exists():
        existing = target_path.read_text(encoding="utf-8")
        if existing == rendered:
            return FileAction(target_path, "skipped", reason="content identical")

    if dry_run:
        return FileAction(
            target_path,
            "would-create" if not target_path.exists() else "would-replace",
            reason=f"render from {template_path.name}",
            diff_lines=len(rendered.splitlines()),
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(rendered, encoding="utf-8")
    return FileAction(
        target_path,
        "created" if not target_path.exists() else "replaced",
        reason=f"render from {template_path.name}",
        diff_lines=len(rendered.splitlines()),
    )


# ---------------------------------------------------------------------------
# Template directory walk
# ---------------------------------------------------------------------------


def list_template_files(template_root: Path) -> list[Path]:
    """Return all files under template_root (recursive). Excludes __pycache__/.git."""
    files: list[Path] = []
    for p in sorted(template_root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and ".git" not in p.parts:
            files.append(p)
    return files


def template_to_target(template_path: Path, template_root: Path, target_root: Path) -> Path:
    """Map a template file path to target path, stripping `.tmpl` suffix."""
    rel = template_path.relative_to(template_root)
    name = rel.name
    if name.endswith(".tmpl"):
        name = name[: -len(".tmpl")]
    return target_root / rel.parent / name


# ---------------------------------------------------------------------------
# Detection: language + tier
# ---------------------------------------------------------------------------


def detect_language(repo_root: Path) -> str:
    """Detect language from manifest at root.

    Returns 'python' | 'typescript' | 'go' | 'rust' | 'polyglot' | 'unknown'.
    """
    has_pyproject = (repo_root / "pyproject.toml").exists()
    has_package = (repo_root / "package.json").exists()
    has_gomod = (repo_root / "go.mod").exists()
    has_cargo = (repo_root / "Cargo.toml").exists()

    detected = []
    if has_pyproject:
        detected.append("python")
    if has_package:
        detected.append("typescript")
    if has_gomod:
        detected.append("go")
    if has_cargo:
        detected.append("rust")

    if len(detected) == 0:
        return "unknown"
    if len(detected) == 1:
        return detected[0]
    return "polyglot"


def is_psr_in_pyproject(language: str) -> bool:
    """Per repo-structure.md: Python repos use [tool.semantic_release] in pyproject.toml.
    Non-Python use semantic-release.toml standalone.
    """
    return language == "python"
