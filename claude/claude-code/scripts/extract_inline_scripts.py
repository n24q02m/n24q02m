#!/usr/bin/env python3
"""Extract inline code blocks from a skill's .md files into standalone scripts.

For use in distillation pipeline P2 — personal skills only.

Spec: .superpower/n24q02m/specs/2026-05-05-claude-config-distillation-pipeline-design.md
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LANG_TO_EXT = {
    "bash": ".sh", "sh": ".sh", "zsh": ".sh",
    "python": ".py", "py": ".py",
    "typescript": ".ts", "ts": ".ts",
    "javascript": ".js", "js": ".js",
}

CODE_BLOCK_RE = re.compile(r"^```(\w+)\n(.*?)^```", re.MULTILINE | re.DOTALL)


@dataclass
class ExtractedBlock:
    md_path: Path
    seq: int
    lang: str
    content: str
    script_path: Path  # relative to skill dir
    script_path_abs: Path  # absolute


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract inline code blocks into scripts/")
    parser.add_argument("skill_dir", type=Path, help="Personal skill directory")
    parser.add_argument("--dry-run", action="store_true", help="List blocks, don't extract")
    args = parser.parse_args()

    blocks = extract_skill(args.skill_dir, dry_run=args.dry_run)
    print(f"Extracted {len(blocks)} blocks from {args.skill_dir}")


def extract_skill(skill_dir: Path, *, dry_run: bool = False) -> list[ExtractedBlock]:
    """Walk skill_dir for *.md files, extract code blocks to scripts/<name>.{ext}."""
    if not skill_dir.exists():
        return []

    scripts_dir = skill_dir / "scripts"
    blocks: list[ExtractedBlock] = []

    md_files = sorted(skill_dir.rglob("*.md"))
    for md_path in md_files:
        # Skip if md_path itself is in scripts/ (defensive)
        if "scripts" in md_path.parts:
            continue

        content = md_path.read_text(encoding="utf-8", errors="replace")
        topic = "skill" if md_path.name == "SKILL.md" else md_path.stem

        new_content = content
        seq_in_file = 0
        offset = 0  # cumulative index shift from replacements

        for match in CODE_BLOCK_RE.finditer(content):
            lang = match.group(1).lower()
            ext = LANG_TO_EXT.get(lang)
            if ext is None:
                continue  # skip unsupported lang (markdown, json, yaml, etc.)

            seq_in_file += 1
            block_content = match.group(2)
            line_count = block_content.count("\n")

            script_name = f"{topic}-{seq_in_file}{ext}"
            script_rel = Path("scripts") / script_name
            script_abs = scripts_dir / script_name

            blocks.append(ExtractedBlock(
                md_path=md_path,
                seq=seq_in_file,
                lang=lang,
                content=block_content,
                script_path=script_rel,
                script_path_abs=script_abs,
            ))

            if not dry_run:
                pointer = f"**Run**: `{script_rel.as_posix()}` — extracted script ({line_count} lines)"
                start = match.start() + offset
                end = match.end() + offset
                new_content = new_content[:start] + pointer + new_content[end:]
                offset += len(pointer) - (end - start)

        if not dry_run and seq_in_file > 0:
            md_path.write_text(new_content, encoding="utf-8")

    if not dry_run and blocks:
        scripts_dir.mkdir(parents=True, exist_ok=True)
        for b in blocks:
            b.script_path_abs.write_text(b.content, encoding="utf-8")
            if b.script_path_abs.suffix == ".sh":
                try:
                    b.script_path_abs.chmod(0o755)
                except (OSError, NotImplementedError):
                    pass

    return blocks


if __name__ == "__main__":
    main()
