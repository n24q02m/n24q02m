#!/usr/bin/env python3
"""Revert P2 extraction — restore inline code blocks in .md from extracted scripts.

For each <skill>/scripts/<topic>-<seq>.<ext> file:
1. Find <skill>/<path>/<topic>.md (or SKILL.md if topic == 'skill')
2. Find pointer line referencing the script
3. Replace pointer with original ```<lang>\\n<content>\\n``` block
4. Delete extracted script file
5. Remove empty scripts/ dir if no files left

Usage: python revert_inline_scripts.py <skill_dir>
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


EXT_TO_LANG = {
    ".sh": "bash",
    ".py": "python",
    ".ts": "typescript",
    ".js": "javascript",
}

POINTER_RE = re.compile(
    r"\*\*Run\*\*: `scripts/([^`]+)` — extracted script \(\d+ lines\)"
)


def revert_skill(skill_dir: Path) -> int:
    """Revert P2 extraction for skill_dir. Returns count of restored blocks."""
    if not skill_dir.exists():
        return 0
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return 0

    restored = 0
    md_files = sorted(skill_dir.rglob("*.md"))
    for md_path in md_files:
        if "scripts" in md_path.parts:
            continue
        content = md_path.read_text(encoding="utf-8", errors="replace")
        new_content = content
        offset = 0

        for match in POINTER_RE.finditer(content):
            script_name = match.group(1)
            script_path = scripts_dir / script_name
            if not script_path.exists():
                continue
            ext = script_path.suffix
            lang = EXT_TO_LANG.get(ext)
            if lang is None:
                continue

            script_content = script_path.read_text(encoding="utf-8", errors="replace")
            # Ensure trailing newline before ``` close
            if not script_content.endswith("\n"):
                script_content += "\n"

            block = f"```{lang}\n{script_content}```"

            start = match.start() + offset
            end = match.end() + offset
            new_content = new_content[:start] + block + new_content[end:]
            offset += len(block) - (end - start)

            script_path.unlink()
            restored += 1

        if new_content != content:
            md_path.write_text(new_content, encoding="utf-8")

    # Remove scripts/ if empty (or only __pycache__)
    if scripts_dir.exists():
        leftover = [p for p in scripts_dir.iterdir() if p.name != "__pycache__"]
        if not leftover:
            try:
                pycache = scripts_dir / "__pycache__"
                if pycache.exists():
                    for p in pycache.iterdir():
                        p.unlink()
                    pycache.rmdir()
                scripts_dir.rmdir()
            except OSError:
                pass

    return restored


def main() -> None:
    parser = argparse.ArgumentParser(description="Revert P2 extraction in a skill dir")
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()
    n = revert_skill(args.skill_dir)
    print(f"Restored {n} blocks in {args.skill_dir}")


if __name__ == "__main__":
    main()
