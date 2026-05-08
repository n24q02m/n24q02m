#!/usr/bin/env python3
"""Scaffold a new empty repo to n24q02m Tier 1 standards.

Usage:
    python init.py --name=foo --owner=n24q02m --lang=python --tier=1 \\
                   --description="Bold one-liner about the project" \\
                   [--mcp] [--target=<dir>] [--force]

Creates:
- All 16 shared/ template files (LICENSE, README, CONTRIBUTING, etc.)
- All 5 per-language partials (.mise.toml, .pre-commit-config, ci.yml, cd.yml, Dockerfile)
- For non-Python: standalone semantic-release.toml
- Initializes git if not already a git repo

Does NOT create:
- pyproject.toml / package.json / Cargo.toml / go.mod (run `uv init`/`npm init`/etc. first)

After init, run language-specific manifest tool, then `apply.py` to inject
PSR config into the new manifest (Python only) or to verify.
"""

from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib_templating import (  # type: ignore[import-not-found]
    ApplyReport,
    is_psr_in_pyproject,
    list_template_files,
    render_and_write,
    template_to_target,
)

TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scaffold new repo to Tier 1 standards")
    p.add_argument("--name", required=True, help="Repo name (e.g. foo-mcp)")
    p.add_argument("--owner", default="n24q02m", help="GitHub owner (default n24q02m)")
    p.add_argument(
        "--lang",
        required=True,
        choices=["python", "typescript", "go"],
        help="Primary language",
    )
    p.add_argument("--tier", default="1", choices=["1", "2"], help="Tier (default 1)")
    p.add_argument("--description", required=True, help="Bold one-liner about the project")
    p.add_argument(
        "--mcp",
        action="store_true",
        help="Also scaffold server.json + .claude-plugin/plugin.json stubs (MCP server)",
    )
    p.add_argument(
        "--target",
        default=".",
        help="Target directory (default cwd; created if absent)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Allow scaffold into non-empty directory (overwrites conflicting files)",
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def build_variables(args: argparse.Namespace) -> dict[str, str]:
    name = args.name
    return {
        "repo_name": name,
        "repo_name_underscore": name.replace("-", "_"),
        "repo_name_upper": name.replace("-", "_").upper(),
        "owner": args.owner,
        "description": args.description,
        "tier": args.tier,
        "language": args.lang,
        "year": str(datetime.datetime.now(datetime.UTC).year),
        "is_mcp": "true" if args.mcp else "false",
        "homepage_url": f"https://{name}.n24q02m.com",
    }


def ensure_target_ready(target: Path, force: bool) -> None:
    """Validate target dir is empty (or --force)."""
    if not target.exists():
        target.mkdir(parents=True)
        return
    if not target.is_dir():
        raise SystemExit(f"--target path {target} exists but is not a directory")
    # Allow .git/ to exist (fresh git init); reject other files unless --force
    contents = [p for p in target.iterdir() if p.name != ".git"]
    if contents and not force:
        raise SystemExit(
            f"--target {target} is not empty (has {len(contents)} entries). "
            "Use --force to scaffold anyway."
        )


def init_git(target: Path) -> None:
    """Run `git init` if .git/ doesn't exist."""
    if (target / ".git").exists():
        return
    subprocess.run(["git", "init", str(target)], check=True, capture_output=True)


def scaffold_shared(variables: dict[str, str], target: Path, *, dry_run: bool) -> ApplyReport:
    """Render all templates/shared/* into target."""
    report = ApplyReport()
    shared_root = TEMPLATE_ROOT / "shared"
    for tpl in list_template_files(shared_root):
        target_file = template_to_target(tpl, shared_root, target)
        action = render_and_write(tpl, target_file, variables, dry_run=dry_run, overwrite=True)
        report.add(action)
    return report


def scaffold_per_language(
    variables: dict[str, str], target: Path, language: str, *, dry_run: bool
) -> ApplyReport:
    """Render all templates/per-language/<lang>/* into target."""
    report = ApplyReport()
    lang_root = TEMPLATE_ROOT / "per-language" / language
    if not lang_root.exists():
        report.errors.append(f"per-language/{language}/ not found in templates")
        return report
    for tpl in list_template_files(lang_root):
        target_file = template_to_target(tpl, lang_root, target)
        action = render_and_write(tpl, target_file, variables, dry_run=dry_run, overwrite=True)
        report.add(action)
    return report


def scaffold_psr_config(
    variables: dict[str, str], target: Path, language: str, *, dry_run: bool
) -> ApplyReport:
    """Place PSR config:
    - Python: defer to apply.py to inject [tool.semantic_release] into pyproject.toml after `uv init`
    - Non-Python: render standalone semantic-release.toml
    """
    report = ApplyReport()
    if is_psr_in_pyproject(language):
        # Python: PSR config goes in pyproject.toml — wait for user `uv init`
        return report
    tpl = TEMPLATE_ROOT / "semantic-release.toml.tmpl"
    target_file = target / "semantic-release.toml"
    action = render_and_write(tpl, target_file, variables, dry_run=dry_run, overwrite=True)
    report.add(action)
    return report


def scaffold_mcp_extras(
    variables: dict[str, str], target: Path, *, dry_run: bool
) -> ApplyReport:
    """Optional MCP server-specific files: server.json + .claude-plugin/plugin.json stubs."""
    report = ApplyReport()
    name = variables["repo_name"]
    description = variables["description"]
    owner = variables["owner"]

    server_json = target / "server.json"
    if not server_json.exists() and not dry_run:
        import json

        server_json.write_text(
            json.dumps(
                {
                    "$schema": "https://static.modelcontextprotocol.io/schemas/2025-07-09/server.schema.json",
                    "name": f"io.github.{owner}/{name}",
                    "description": description,
                    "version": "0.1.0",
                    "repository": {
                        "url": f"https://github.com/{owner}/{name}",
                        "source": "github",
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    plugin_dir = target / ".claude-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_json = plugin_dir / "plugin.json"
    if not plugin_json.exists() and not dry_run:
        import json

        plugin_json.write_text(
            json.dumps(
                {
                    "name": name,
                    "version": "0.1.0",
                    "description": description,
                    "mcpServers": {
                        name: {"command": "uvx", "args": ["--python", "3.13", name]}
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    from _lib_templating import FileAction  # type: ignore[import-not-found]

    if not dry_run:
        report.add(FileAction(server_json, "created", "MCP server stub"))
        report.add(FileAction(plugin_json, "created", "Claude plugin stub"))
    return report


def print_next_steps(language: str, target: Path) -> None:
    print(f"\n{'=' * 60}")
    print(f"Repo scaffolded at: {target.resolve()}")
    print(f"{'=' * 60}\n")
    print("Next steps:")
    if language == "python":
        print(f"  cd {target}")
        print("  uv init                                # creates pyproject.toml")
        print(
            "  python <profile-repo>/scripts/repo-bootstrap/apply.py "
            "--repo-root=.   # injects [tool.semantic_release] into pyproject"
        )
    elif language == "typescript":
        print(f"  cd {target}")
        print("  bun init                               # creates package.json")
        print("  # PSR config already at semantic-release.toml")
    elif language == "go":
        print(f"  cd {target}")
        print("  go mod init github.com/<owner>/<name>  # creates go.mod")
        print("  # PSR config already at semantic-release.toml")
    print()
    print("Then create initial commit:")
    print('  git add . && git commit -m "feat: initial scaffold from repo-bootstrap"')


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    variables = build_variables(args)
    target = Path(args.target).resolve()

    if not args.dry_run:
        ensure_target_ready(target, args.force)
        init_git(target)

    full_report = ApplyReport()

    full_report.actions.extend(
        scaffold_shared(variables, target, dry_run=args.dry_run).actions
    )
    full_report.actions.extend(
        scaffold_per_language(variables, target, args.lang, dry_run=args.dry_run).actions
    )
    full_report.actions.extend(
        scaffold_psr_config(variables, target, args.lang, dry_run=args.dry_run).actions
    )
    if args.mcp:
        full_report.actions.extend(
            scaffold_mcp_extras(variables, target, dry_run=args.dry_run).actions
        )

    print(f"\nSummary: {full_report.summary()}")
    if full_report.errors:
        print("\nErrors:")
        for e in full_report.errors:
            print(f"  - {e}")
        return 1

    if not args.dry_run:
        print_next_steps(args.lang, target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
