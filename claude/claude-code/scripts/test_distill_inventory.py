"""Tests for distill_inventory.py — uses tmp_path fixtures (no real ~/.claude mutation)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from distill_inventory import SCHEMA_VERSION, build_inventory


def test_build_inventory_minimal(tmp_path: Path) -> None:
    inventory = build_inventory(tmp_path)
    assert inventory["schema_version"] == SCHEMA_VERSION
    # On Windows, tmp_path lives under $HOME (AppData/Local/Temp), so the home
    # prefix is anonymized to `<home>`. On POSIX systems tmp_path is under /tmp
    # which is outside $HOME, so the path is returned as-is.
    home_str = str(Path.home())
    if str(tmp_path).startswith(home_str):
        assert inventory["claude_dir"] == str(tmp_path).replace(home_str, "<home>", 1)
        assert home_str not in inventory["claude_dir"]
    else:
        assert inventory["claude_dir"] == str(tmp_path)
    assert "generated_at" in inventory


from distill_inventory import MemoryAnalyzer


def test_memory_analyzer_classifies_session_transcript(tmp_path: Path) -> None:
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "session-abc-transcript.md").write_text("x" * 1000)
    (memory / "feedback_no_secrets.md").write_text("y" * 500)
    (memory / "MEMORY.md").write_text("index")

    analyzer = MemoryAnalyzer(memory)
    result = analyzer.analyze()

    assert result["total_files"] == 3
    assert result["session_transcripts_count"] == 1
    assert result["feedback_files_count"] == 1


def test_memory_analyzer_clusters_by_prefix(tmp_path: Path) -> None:
    memory = tmp_path / "memory"
    memory.mkdir()
    for theme in ["no_secrets", "no_open_ports", "no_workaround", "verify_done", "verify_completeness"]:
        (memory / f"feedback_{theme}.md").write_text("x")

    analyzer = MemoryAnalyzer(memory)
    result = analyzer.analyze()

    clusters = result["clusters"]
    assert clusters["no"]["count"] == 3
    assert clusters["verify"]["count"] == 2
    assert sorted(clusters["no"]["files"]) == [
        "feedback_no_open_ports.md",
        "feedback_no_secrets.md",
        "feedback_no_workaround.md",
    ]


from distill_inventory import RuleAnalyzer


def test_rule_analyzer_parses_claude_md(tmp_path: Path) -> None:
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("""
<important if="condition A">
  rule body 1
</important>
<important if="condition B">
  rule body 2 references memory `feedback_xyz.md` and skill `infra-devops`.
</important>
This is a "for now" workaround.
""", encoding="utf-8")

    analyzer = RuleAnalyzer(claude_md)
    result = analyzer.analyze()

    assert result["claude_md_size_bytes"] == claude_md.stat().st_size
    assert result["important_if_blocks"] == 2
    assert result["memory_references"] == 1
    assert result["skill_references"] == 1
    assert result["code_blocks"] == 0
    assert "for now" in str(result["quick_fix_pattern_matches"]).lower()


def test_rule_analyzer_detects_size_limit_breach(tmp_path: Path) -> None:
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("x" * 41000)  # >40KB

    analyzer = RuleAnalyzer(claude_md)
    result = analyzer.analyze()

    assert result["claude_md_size_bytes"] == 41000
    assert result["claude_md_size_kb"] == 41
    assert result["exceeds_40kb_limit"] is True


from distill_inventory import SkillAnalyzer


def test_skill_analyzer_extracts_metadata(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skills.mkdir()

    skill_dir = skills / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: Test skill description
---
# My Skill

```bash
echo hello
```
""", encoding="utf-8")
    refs = skill_dir / "references"
    refs.mkdir()
    (refs / "topic-a.md").write_text("ref content")
    (refs / "topic-b.md").write_text("ref content")

    analyzer = SkillAnalyzer(skills)
    result = analyzer.analyze()

    assert len(result) == 1
    skill = result[0]
    assert skill["name"] == "my-skill"
    assert skill["lines"] > 0
    assert skill["references_count"] == 2
    assert skill["inline_code_blocks"] == 1


def test_skill_analyzer_detects_gstack_leftover(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skills.mkdir()

    qa_dir = skills / "qa"
    qa_dir.mkdir()
    (qa_dir / "SKILL.md").write_text("""---
name: qa
description: QA testing skill (gstack)
---
# QA
""", encoding="utf-8")

    analyzer = SkillAnalyzer(skills)
    result = analyzer.analyze()
    skill = result[0]
    assert skill["is_plugin_leftover"] is True
    assert skill["leftover_source_plugin"] == "gstack"


from distill_inventory import PluginAnalyzer, ScriptDetector


def test_plugin_analyzer_enumerates_plugins(tmp_path: Path) -> None:
    cache = tmp_path / "plugins" / "cache"
    cache.mkdir(parents=True)

    sp_dir = cache / "claude-plugins-official" / "superpowers" / "5.1.0"
    sp_dir.mkdir(parents=True)
    skills_dir = sp_dir / "skills"
    skills_dir.mkdir()
    (skills_dir / "brainstorming").mkdir()
    (skills_dir / "brainstorming" / "SKILL.md").write_text("---\nname: brainstorming\n---")
    agents_dir = sp_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "code-reviewer.md").write_text("agent")

    analyzer = PluginAnalyzer(cache)
    result = analyzer.analyze()

    assert len(result) == 1
    plugin = result[0]
    assert plugin["name"] == "superpowers"
    assert plugin["marketplace"] == "claude-plugins-official"
    assert plugin["version"] == "5.1.0"
    assert plugin["skills_count"] == 1
    assert plugin["agents_count"] == 1


def test_script_detector_aggregates_inline_blocks(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skill_a = skills / "alpha"
    skill_a.mkdir(parents=True)
    (skill_a / "SKILL.md").write_text("```bash\necho A\n```\n```python\nprint(1)\n```")

    skill_b = skills / "beta"
    skill_b.mkdir()
    (skill_b / "SKILL.md").write_text("```bash\necho B\n```")

    detector = ScriptDetector(skills)
    result = detector.analyze()

    assert result["inline_blocks_total"] == 3
    assert result["by_skill"] == {"alpha": 2, "beta": 1}


def test_build_inventory_picks_largest_memory_dir(tmp_path: Path) -> None:
    """When multiple project memory dirs exist, pick the one with most files (active)."""
    stale = tmp_path / "projects" / "stale-legacy" / "memory"
    stale.mkdir(parents=True)
    for i in range(3):
        (stale / f"feedback_old_{i}.md").write_text("x")

    active = tmp_path / "projects" / "active-cwd" / "memory"
    active.mkdir(parents=True)
    for i in range(20):
        (active / f"feedback_new_{i}.md").write_text("x")

    inventory = build_inventory(tmp_path)
    assert inventory["memory"]["total_files"] == 20  # active picked, not stale


def test_build_inventory_orchestrates_all_layers(tmp_path: Path) -> None:
    # Setup minimal but realistic ~/.claude
    memory = tmp_path / "projects" / "sess1" / "memory"
    memory.mkdir(parents=True)
    (memory / "feedback_no_secrets.md").write_text("x")
    (memory / "session-abc.md").write_text("y" * 1000)

    skills = tmp_path / "skills"
    skill = skills / "personal"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: personal\n---\n# Personal\n```bash\necho 1\n```")

    cache = tmp_path / "plugins" / "cache" / "test-mp" / "test-plugin" / "1.0.0"
    cache.mkdir(parents=True)
    (cache / "skills").mkdir()

    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("<important if='x'>rule</important>")

    inventory = build_inventory(tmp_path)

    assert inventory["schema_version"] == SCHEMA_VERSION
    assert inventory["memory"]["total_files"] == 2
    assert inventory["memory"]["session_transcripts_count"] == 1
    assert inventory["rule"]["important_if_blocks"] == 1
    assert len(inventory["skills"]) == 1
    assert inventory["skills"][0]["name"] == "personal"
    assert len(inventory["plugins"]) == 1
    assert inventory["scripts_layer"]["inline_blocks_total"] == 1


def test_build_inventory_anonymizes_home_path(tmp_path: Path, monkeypatch) -> None:
    """claude_dir output should not leak username when under home dir."""
    monkeypatch.setattr("distill_inventory.Path.home", lambda: tmp_path.parent)
    inventory = build_inventory(tmp_path)
    home_str = str(tmp_path.parent)
    assert home_str not in inventory["claude_dir"]
    assert "<home>" in inventory["claude_dir"]


def test_rule_analyzer_handles_non_utf8(tmp_path: Path) -> None:
    """RuleAnalyzer should not crash on non-UTF8 CLAUDE.md content."""
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_bytes(b"\xff\xfe<important if='x'>rule</important>")  # non-UTF8 BOM-like
    analyzer = RuleAnalyzer(claude_md)
    result = analyzer.analyze()
    assert result["important_if_blocks"] == 1  # should still parse what's parseable
