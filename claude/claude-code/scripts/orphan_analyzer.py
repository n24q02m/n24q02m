#!/usr/bin/env python3
"""Analyze orphan feedback memory files for P3 promotion candidates.

Categorizes each feedback_*.md file as STALE / RECURRING / INCIDENT / TOPIC_<X>
based on content signals + cross-reference with CLAUDE.md and skill .md files.

Output: JSON report for user-driven promotion batches.

Spec: .superpower/n24q02m/specs/2026-05-05-claude-config-distillation-pipeline-design.md
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOPIC_TO_SKILL = {
    "relay": "mcp-dev",
    "mcp": "mcp-dev",
    "e2e": "mcp-dev",
    "stdio": "mcp-dev",
    "real": "mcp-dev",
    "skret": "infra-devops",
    "psr": "infra-devops",
    "cf": "infra-devops",
    "wet": "mcp-dev",
}

RECURRING_PATTERNS = [
    r"\bM\s*[=>]\s*\d+\b",
    r"\boccurred\s+\d+\s+times\b",
    r"\b\d+\s+times\b",
    r"incidents?\s+\d{1,2}/\d{1,2}.*?\+\s*\d{1,2}/\d{1,2}",
    r"violation\s+\d{4}-\d{2}-\d{2}.*?\+\s*\d{4}-\d{2}-\d{2}",
    r"sessions?\s*[<:]?\s*[\w\-]+\s*\+\s*[\w\-]+",
]


@dataclass
class OrphanEntry:
    file: str
    size_bytes: int
    topic_prefix: str
    referenced_in_claude_md: bool
    referenced_in_skill: list[str] = field(default_factory=list)
    category: str = "INCIDENT"
    recurring_evidence: list[str] = field(default_factory=list)
    stale_evidence: list[str] = field(default_factory=list)
    promotion_target: str = ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze feedback orphans")
    parser.add_argument("--memory-dir", type=Path,
                        default=Path("C:/Users/n24q02m-wlap/.claude/projects/C--Users-n24q02m-wlap-projects/memory"))
    parser.add_argument("--claude-md", type=Path,
                        default=Path("C:/Users/n24q02m-wlap/.claude/CLAUDE.md"))
    parser.add_argument("--skills-dir", type=Path,
                        default=Path("C:/Users/n24q02m-wlap/.claude/skills"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = analyze(args.memory_dir, args.claude_md, args.skills_dir)
    args.output.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Report written: {args.output}")
    print(f"Total feedback: {report['summary']['total']}")
    print(f"Orphan: {report['summary']['orphan']}")
    print(f"By category: {report['summary']['by_category']}")


def analyze(memory_dir: Path, claude_md: Path, skills_dir: Path) -> dict[str, Any]:
    """Analyze feedback files, categorize each, return JSON-serializable report."""
    if not memory_dir.exists():
        return {"summary": {"total": 0, "orphan": 0, "by_category": {}}, "entries": []}

    feedback_files = sorted(memory_dir.glob("feedback_*.md"))
    claude_content = claude_md.read_text(encoding="utf-8", errors="replace") if claude_md.exists() else ""

    skill_md_files: list[Path] = []
    if skills_dir.exists():
        skill_md_files = list(skills_dir.rglob("*.md"))

    entries: list[OrphanEntry] = []
    for fb in feedback_files:
        entries.append(_classify(fb, claude_content, skill_md_files))

    by_category: dict[str, int] = {}
    orphan_count = 0
    for e in entries:
        by_category[e.category] = by_category.get(e.category, 0) + 1
        if not e.referenced_in_claude_md and not e.referenced_in_skill:
            orphan_count += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(entries),
            "orphan": orphan_count,
            "by_category": by_category,
        },
        "entries": [asdict(e) for e in entries],
    }


def _classify(fb_path: Path, claude_content: str, skill_md_files: list[Path]) -> OrphanEntry:
    name = fb_path.name
    body = fb_path.read_text(encoding="utf-8", errors="replace")

    stem = fb_path.stem.removeprefix("feedback_")
    topic = stem.split("_")[0]

    referenced_in_claude = name in claude_content
    referenced_in_skill: list[str] = []
    for skill_md in skill_md_files:
        try:
            if name in skill_md.read_text(encoding="utf-8", errors="replace"):
                for part in skill_md.parts:
                    if part == "skills":
                        idx = skill_md.parts.index(part)
                        if idx + 1 < len(skill_md.parts):
                            referenced_in_skill.append(skill_md.parts[idx + 1])
                            break
        except OSError:
            continue

    entry = OrphanEntry(
        file=name,
        size_bytes=fb_path.stat().st_size,
        topic_prefix=topic,
        referenced_in_claude_md=referenced_in_claude,
        referenced_in_skill=sorted(set(referenced_in_skill)),
    )

    for pattern in RECURRING_PATTERNS:
        for m in re.finditer(pattern, body, re.IGNORECASE):
            entry.recurring_evidence.append(m.group())
            if len(entry.recurring_evidence) >= 5:
                break
        if len(entry.recurring_evidence) >= 5:
            break

    stale_keywords = ["DEPRECATED", "SUPERSEDED", "obsolete", "no longer valid"]
    for kw in stale_keywords:
        if kw.lower() in body.lower():
            entry.stale_evidence.append(kw)

    if entry.stale_evidence:
        entry.category = "STALE"
    elif entry.recurring_evidence:
        entry.category = "RECURRING"
    else:
        entry.category = "INCIDENT"

    target_skill = TOPIC_TO_SKILL.get(topic)
    if target_skill:
        entry.promotion_target = target_skill
        if entry.category == "RECURRING":
            entry.category = f"TOPIC_{target_skill}"

    return entry


if __name__ == "__main__":
    main()
