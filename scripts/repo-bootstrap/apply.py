#!/usr/bin/env python3
"""Idempotent retrofit of n24q02m Tier 1 standards onto an existing repo.

Usage:
    python apply.py [--repo-root=.] [--dry-run] [--force]

Detects language via root manifests (pyproject.toml / package.json / go.mod
/ Cargo.toml). For Python repos, deep-merges [tool.semantic_release] config
into existing pyproject.toml. For non-Python, places semantic-release.toml
standalone.

Merge strategies (per Spec G2):
- skip-if-exists  : leave user content alone (AGENTS, .gitignore, .skret.yaml,
                    .pr_agent.toml, .pre-commit-config)
- atomic-replace  : overwrite if hash differs, prompt confirm interactive,
                    --force to overwrite without prompt
                    (LICENSE, CODE_OF_CONDUCT, SECURITY, CONTRIBUTING,
                     ISSUE_TEMPLATE/*, PULL_REQUEST_TEMPLATE, best_practices,
                     rulesets/main.json)
- compose-only    : TOML/JSON deep-merge — insert template keys, preserve user
                    keys, error on value conflict
                    (renovate.json, .mise.toml, pyproject.toml [tool.semantic_release])
- managed-region  : rewrite within <!-- MANAGED-START: <key> --> markers
                    (README.md cross-promo block, CHANGELOG.md headers,
                     ci.yml/cd.yml standard jobs)

Re-runnable: idempotent on aligned files (no diff = no-op).
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import tomllib
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib_templating import (  # type: ignore[import-not-found]
    ApplyReport,
    FileAction,
    detect_language,
    file_hash,
    is_psr_in_pyproject,
    list_template_files,
    render_and_write,
    safe_render,
    template_to_target,
    text_hash,
)

TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"


# ---------------------------------------------------------------------------
# Merge strategy classification (per filename)
# ---------------------------------------------------------------------------

SKIP_IF_EXISTS = {
    "AGENTS.md",
    ".gitignore",
    ".skret.yaml",
    ".pr_agent.toml",
    ".pre-commit-config.yaml",
    ".mise.toml",
    "README.md",
    "CHANGELOG.md",
}

ATOMIC_REPLACE = {
    "LICENSE",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "PULL_REQUEST_TEMPLATE.md",
    "best_practices.md",
    "main.json",  # rulesets/main.json
    "bug_report.md",
    "feature_request.md",
    "CODEOWNERS",
    "Dockerfile",
    "ci.yml",
    "cd.yml",
    "semantic-release.toml",
}

COMPOSE_ONLY = {
    "renovate.json",
}

# Note: pyproject.toml is handled separately (PSR section deep-merge for Python)


def classify(target_filename: str) -> str:
    """Return merge strategy for a target file's basename."""
    if target_filename in SKIP_IF_EXISTS:
        return "skip-if-exists"
    if target_filename in COMPOSE_ONLY:
        return "compose-only"
    if target_filename in ATOMIC_REPLACE:
        return "atomic-replace"
    return "atomic-replace"  # default conservative


# ---------------------------------------------------------------------------
# Compose-only deep-merge (JSON / TOML)
# ---------------------------------------------------------------------------


def deep_merge(target: dict, src: dict, path: str = "") -> tuple[dict, list[str]]:
    """Deep-merge src into target. Returns (merged, conflicts).

    Insert src keys not in target. Preserve target's keys. Error on value
    conflict (different non-dict values for same key path).
    """
    conflicts: list[str] = []
    out = dict(target)
    for k, v in src.items():
        path_k = f"{path}.{k}" if path else k
        if k not in out:
            out[k] = v
        elif isinstance(out[k], dict) and isinstance(v, dict):
            sub, sub_conflicts = deep_merge(out[k], v, path_k)
            out[k] = sub
            conflicts.extend(sub_conflicts)
        elif out[k] != v:
            # Value conflict — preserve user's, log
            conflicts.append(f"{path_k}: user={out[k]!r} vs template={v!r} (kept user)")
    return out, conflicts


def merge_json_file(
    template_path: Path, target_path: Path, *, dry_run: bool
) -> FileAction:
    """Compose-only deep-merge JSON file."""
    template_data = json.loads(template_path.read_text(encoding="utf-8"))
    if target_path.exists():
        try:
            target_data = json.loads(target_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return FileAction(target_path, "skipped", f"existing JSON invalid: {e}")
        merged, conflicts = deep_merge(target_data, template_data)
        new_text = json.dumps(merged, indent=2) + "\n"
        if new_text == target_path.read_text(encoding="utf-8"):
            return FileAction(target_path, "skipped", "merge no-op")
        if dry_run:
            return FileAction(
                target_path, "would-merge", f"json merge ({len(conflicts)} conflicts kept user)"
            )
        target_path.write_text(new_text, encoding="utf-8")
        return FileAction(
            target_path, "merged", f"json deep-merge ({len(conflicts)} conflicts kept user)"
        )
    if dry_run:
        return FileAction(target_path, "would-create", "json template")
    target_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    return FileAction(target_path, "created", "json template")


# ---------------------------------------------------------------------------
# PSR pyproject merge (Python only)
# ---------------------------------------------------------------------------


_PSR_PYPROJECT_BLOCK = """
[tool.semantic_release]
tag_format = "v{version}"
commit_message = "feat(release): v{version} [skip ci]"
major_on_zero = false
allow_zero_version = true
version_toml = ["pyproject.toml:project.version"]

[tool.semantic_release.changelog]
changelog_file = "CHANGELOG.md"

[tool.semantic_release.remote]
type = "github"
"""


def merge_psr_into_pyproject(
    repo_root: Path, *, dry_run: bool
) -> FileAction:
    """Inject [tool.semantic_release] into existing pyproject.toml."""
    pp = repo_root / "pyproject.toml"
    if not pp.exists():
        return FileAction(pp, "skipped", "pyproject.toml absent — run `uv init` first")
    text = pp.read_text(encoding="utf-8")
    try:
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        return FileAction(pp, "skipped", f"existing pyproject invalid TOML: {e}")
    if "tool" in parsed and "semantic_release" in parsed.get("tool", {}):
        return FileAction(pp, "skipped", "[tool.semantic_release] already present")
    new_text = text.rstrip("\n") + "\n" + _PSR_PYPROJECT_BLOCK
    if dry_run:
        return FileAction(pp, "would-merge", "append [tool.semantic_release]")
    pp.write_text(new_text, encoding="utf-8")
    return FileAction(pp, "merged", "appended [tool.semantic_release]")


# ---------------------------------------------------------------------------
# Atomic-replace + skip + interactive prompt
# ---------------------------------------------------------------------------


def apply_atomic_replace(
    template_path: Path,
    target_path: Path,
    variables: dict[str, str],
    *,
    dry_run: bool,
    force: bool,
) -> FileAction:
    """Overwrite if hash differs. Interactive prompt when not force/dry-run."""
    rendered = safe_render(template_path.read_text(encoding="utf-8"), variables)
    new_hash = text_hash(rendered)
    if target_path.exists():
        cur_hash = file_hash(target_path)
        if cur_hash == new_hash:
            return FileAction(target_path, "skipped", "content identical")
        if not force and not dry_run:
            try:
                resp = input(f"Replace {target_path.relative_to(target_path.parents[0])}? [y/N]: ")
            except EOFError:
                resp = "n"
            if resp.lower() != "y":
                return FileAction(target_path, "skipped", "user declined")
        if dry_run:
            return FileAction(
                target_path, "would-replace", f"hash differs ({cur_hash[:8]} → {new_hash[:8]})"
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(rendered, encoding="utf-8")
        return FileAction(target_path, "replaced", "hash differed")
    if dry_run:
        return FileAction(target_path, "would-create", "template render")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(rendered, encoding="utf-8")
    return FileAction(target_path, "created", "template render")


def apply_skip_if_exists(
    template_path: Path,
    target_path: Path,
    variables: dict[str, str],
    *,
    dry_run: bool,
) -> FileAction:
    """Create from template if absent; preserve existing user content."""
    if target_path.exists():
        return FileAction(target_path, "skipped", "exists, user content preserved")
    return render_and_write(template_path, target_path, variables, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Variable detection from existing repo state
# ---------------------------------------------------------------------------


def detect_variables(repo_root: Path, language: str) -> dict[str, str]:
    """Best-effort detection of {{vars}} from existing repo state.

    Falls back to placeholders that user can edit post-apply.
    """
    name = repo_root.name
    description = ""
    owner = "n24q02m"

    # README tagline (line 3 heuristic)
    readme = repo_root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        # Try extract description from first prose line
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith(("#", "<", "[", "!", "|", "-", ">")):
                description = stripped[:200]
                break

    # pyproject project.name (Python)
    if language == "python":
        pp = repo_root / "pyproject.toml"
        if pp.exists():
            try:
                parsed = tomllib.loads(pp.read_text(encoding="utf-8"))
                project = parsed.get("project") or {}
                if project.get("name"):
                    name = project["name"]
                if project.get("description"):
                    description = project["description"]
            except tomllib.TOMLDecodeError:
                pass

    # package.json (TS)
    if language == "typescript":
        pkg = repo_root / "package.json"
        if pkg.exists():
            try:
                d = json.loads(pkg.read_text(encoding="utf-8"))
                if d.get("name"):
                    pkg_name = d["name"]
                    if "/" in pkg_name:
                        name = pkg_name.split("/", 1)[1]
                    else:
                        name = pkg_name
                if d.get("description"):
                    description = d["description"]
            except json.JSONDecodeError:
                pass

    return {
        "repo_name": name,
        "repo_name_underscore": name.replace("-", "_"),
        "repo_name_upper": name.replace("-", "_").upper(),
        "owner": owner,
        "description": description or "(set repo description)",
        "tier": "1",
        "language": language,
        "year": str(datetime.datetime.now(datetime.UTC).year),
        "is_mcp": "false",
        "homepage_url": f"https://{name}.n24q02m.com",
    }


# ---------------------------------------------------------------------------
# Main apply logic
# ---------------------------------------------------------------------------


def apply_template_tree(
    template_root: Path,
    target_root: Path,
    variables: dict[str, str],
    *,
    dry_run: bool,
    force: bool,
) -> ApplyReport:
    report = ApplyReport()
    for tpl in list_template_files(template_root):
        target_file = template_to_target(tpl, template_root, target_root)
        strategy = classify(target_file.name)
        if strategy == "skip-if-exists":
            action = apply_skip_if_exists(tpl, target_file, variables, dry_run=dry_run)
        elif strategy == "compose-only":
            if target_file.suffix == ".json":
                action = merge_json_file(tpl, target_file, dry_run=dry_run)
            else:
                action = apply_atomic_replace(
                    tpl, target_file, variables, dry_run=dry_run, force=force
                )
        else:  # atomic-replace
            action = apply_atomic_replace(
                tpl, target_file, variables, dry_run=dry_run, force=force
            )
        report.add(action)
    return report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Idempotent retrofit of Tier 1 standards onto existing repo"
    )
    p.add_argument("--repo-root", default=".", help="Target repo (default cwd)")
    p.add_argument("--dry-run", action="store_true", help="Print intended diff, no writes")
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite atomic-replace files without confirmation prompts",
    )
    return p.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"ERROR: --repo-root {repo_root} does not exist", file=sys.stderr)
        return 2

    language = detect_language(repo_root)
    if language == "unknown":
        print(
            "ERROR: no language manifest at repo root "
            "(pyproject.toml / package.json / go.mod / Cargo.toml). "
            "Run `uv init` / `npm init` / `go mod init` / `cargo init` first, "
            "OR use init.py for new empty repo.",
            file=sys.stderr,
        )
        return 2

    print(f"Detected language: {language}")
    variables = detect_variables(repo_root, language)
    print(f"Variables: repo_name={variables['repo_name']}, owner={variables['owner']}")

    full_report = ApplyReport()

    # Apply shared/* templates
    full_report.actions.extend(
        apply_template_tree(
            TEMPLATE_ROOT / "shared",
            repo_root,
            variables,
            dry_run=args.dry_run,
            force=args.force,
        ).actions
    )

    # Apply per-language partials
    lang_root = TEMPLATE_ROOT / "per-language" / language
    if lang_root.exists():
        full_report.actions.extend(
            apply_template_tree(
                lang_root,
                repo_root,
                variables,
                dry_run=args.dry_run,
                force=args.force,
            ).actions
        )

    # Apply PSR config
    if is_psr_in_pyproject(language):
        full_report.actions.append(
            merge_psr_into_pyproject(repo_root, dry_run=args.dry_run)
        )
    else:
        # Non-Python: render semantic-release.toml standalone via atomic-replace
        sr_template = TEMPLATE_ROOT / "semantic-release.toml.tmpl"
        sr_target = repo_root / "semantic-release.toml"
        full_report.actions.append(
            apply_atomic_replace(
                sr_template,
                sr_target,
                variables,
                dry_run=args.dry_run,
                force=args.force,
            )
        )

    # Print report
    print(f"\n{'=' * 60}")
    print(f"Apply report — {full_report.summary()}")
    print(f"{'=' * 60}\n")
    for a in full_report.actions:
        try:
            rel = a.path.relative_to(repo_root)
        except ValueError:
            rel = a.path
        print(f"  {a.action:<16} {rel}  ({a.reason})")

    return 1 if full_report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
