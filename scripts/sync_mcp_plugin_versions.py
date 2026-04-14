#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


PLUGIN_NAMES = [
    "wet-mcp",
    "mnemo-mcp",
    "better-notion-mcp",
    "better-email-mcp",
    "better-godot-mcp",
    "better-telegram-mcp",
    "better-code-review-graph",
]

CLAUDE_PLUGINS_RAW_BASE = (
    "https://raw.githubusercontent.com/n24q02m/claude-plugins/main/plugins"
)

SERVER_CELL_PATTERN = re.compile(r"\[([^\]]+)\]")


def fetch_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for plugin_name in PLUGIN_NAMES:
        url = (
            f"{CLAUDE_PLUGINS_RAW_BASE}/{plugin_name}/.claude-plugin/plugin.json"
        )
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = json.load(response)
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc

        version = str(payload.get("version", "")).strip()
        if not version:
            raise RuntimeError(f"Missing version in {url}")
        versions[plugin_name] = version

    return versions


def parse_row_cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def format_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def sync_readme_versions(readme_path: Path, versions: dict[str, str]) -> bool:
    original_text = readme_path.read_text(encoding="utf-8")
    lines = original_text.splitlines()

    header_index = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("| Server |")),
        None,
    )
    if header_index is None:
        raise RuntimeError("Could not find Servers table header in README.md")

    separator_index = header_index + 1
    if separator_index >= len(lines):
        raise RuntimeError("README.md Servers table separator line is missing")

    rows_start = header_index + 2
    rows_end = rows_start
    while rows_end < len(lines) and lines[rows_end].lstrip().startswith("|"):
        rows_end += 1

    original_rows = lines[rows_start:rows_end]
    if not original_rows:
        raise RuntimeError("README.md Servers table has no rows")

    seen_plugins: set[str] = set()
    updated_rows: list[str] = []

    for row in original_rows:
        cells = parse_row_cells(row)
        if len(cells) not in (4, 5):
            raise RuntimeError(
                "Unexpected Servers table format in README.md. "
                f"Expected 4 or 5 columns, got {len(cells)} in row: {row}"
            )

        server_cell = cells[0]
        match = SERVER_CELL_PATTERN.search(server_cell)
        if not match:
            raise RuntimeError(
                "Could not parse plugin name from Servers table row: " f"{row}"
            )

        plugin_name = match.group(1)
        if plugin_name not in versions:
            raise RuntimeError(
                f"Plugin {plugin_name} in README.md not found in source version map"
            )

        if len(cells) == 4:
            description_cell, guide_cell, runtime_cell = cells[1], cells[2], cells[3]
        else:
            description_cell, guide_cell, runtime_cell = cells[2], cells[3], cells[4]

        updated_rows.append(
            format_table_row(
                [
                    server_cell,
                    f"`{versions[plugin_name]}`",
                    description_cell,
                    guide_cell,
                    runtime_cell,
                ]
            )
        )
        seen_plugins.add(plugin_name)

    expected_plugins = set(PLUGIN_NAMES)
    missing_plugins = expected_plugins - seen_plugins
    if missing_plugins:
        raise RuntimeError(
            "README.md is missing expected plugin rows: "
            f"{', '.join(sorted(missing_plugins))}"
        )

    updated_table = [
        "| Server | Version (from claude-plugins) | Description | Agent Setup | Runtime |",
        "|--------|-------------------------------|-------------|-------------|---------|",
        *updated_rows,
    ]

    updated_lines = [
        *lines[:header_index],
        *updated_table,
        *lines[rows_end:],
    ]

    trailing_newline = "\n" if original_text.endswith("\n") else ""
    updated_text = "\n".join(updated_lines) + trailing_newline

    if updated_text == original_text:
        return False

    readme_path.write_text(updated_text, encoding="utf-8")
    return True


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    readme_path = repo_root / "README.md"

    if not readme_path.exists():
        raise RuntimeError(f"README.md not found at: {readme_path}")

    versions = fetch_versions()
    changed = sync_readme_versions(readme_path, versions)

    if changed:
        print("Updated README.md with latest MCP/plugin versions from claude-plugins.")
    else:
        print("README.md is already synced with claude-plugins versions.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)