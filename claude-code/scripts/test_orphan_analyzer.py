"""Tests for orphan_analyzer.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from orphan_analyzer import OrphanEntry, RECURRING_PATTERNS, TOPIC_TO_SKILL, analyze


def test_topic_to_skill_map() -> None:
    assert TOPIC_TO_SKILL["relay"] == "mcp-dev"
    assert TOPIC_TO_SKILL["skret"] == "infra-devops"


def test_recurring_patterns_compile() -> None:
    import re
    for p in RECURRING_PATTERNS:
        re.compile(p)


def test_orphan_entry_dataclass() -> None:
    entry = OrphanEntry(
        file="feedback_test.md",
        size_bytes=1000,
        topic_prefix="test",
        referenced_in_claude_md=False,
    )
    assert entry.category == "INCIDENT"
    assert entry.recurring_evidence == []


def test_analyze_categorizes_orphan_recurring(tmp_path: Path) -> None:
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "feedback_test_recurring.md").write_text(
        "---\nname: test\n---\n\nThis incident occurred 5 times across sessions abc + def.",
        encoding="utf-8"
    )
    (memory / "feedback_test_incident.md").write_text(
        "---\nname: incident\n---\n\nOne-time issue 2026-04-20.",
        encoding="utf-8"
    )
    (memory / "MEMORY.md").write_text("# Index", encoding="utf-8")

    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("Some rules", encoding="utf-8")

    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    report = analyze(memory, claude_md, skills_dir)

    assert report["summary"]["total"] == 2
    assert report["summary"]["orphan"] == 2
    by_cat = report["summary"]["by_category"]
    assert by_cat.get("RECURRING", 0) >= 1


def test_analyze_detects_topic_skill_match(tmp_path: Path) -> None:
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "feedback_relay_form_bug.md").write_text(
        "---\nname: relay bug\n---\n\nMCP relay form bug occurred 3 times.",
        encoding="utf-8"
    )

    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("", encoding="utf-8")

    skills_dir = tmp_path / "skills"
    (skills_dir / "mcp-dev").mkdir(parents=True)

    report = analyze(memory, claude_md, skills_dir)

    entries = report["entries"]
    relay_entry = next(e for e in entries if "relay" in e["file"])
    assert relay_entry["promotion_target"] == "mcp-dev"
    assert relay_entry["category"] in ("TOPIC_mcp-dev", "RECURRING")
