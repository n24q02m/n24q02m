#!/usr/bin/env python3
"""Distill inventory tool — enumerate ~/.claude artifacts.

Generates JSON report of memory / rule / skill / reference / inline-script /
plugin layers for use in distillation pipeline phases P2-P7.

Spec: .superpower/n24q02m/specs/2026-05-05-claude-config-distillation-pipeline-design.md
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"


@dataclass
class MemoryAnalyzer:
    """Analyze memory layer: session transcripts, feedback files, clusters."""

    memory_dir: Path

    def analyze(self) -> dict[str, Any]:
        if not self.memory_dir.exists():
            return {"total_files": 0, "total_size_bytes": 0,
                    "session_transcripts_count": 0, "feedback_files_count": 0,
                    "clusters": {}}

        all_md = sorted(self.memory_dir.glob("*.md"))
        sessions = [f for f in all_md if f.name.startswith("session-")]
        feedbacks = [f for f in all_md if f.name.startswith("feedback_")]

        return {
            "total_files": len(all_md),
            "total_size_bytes": sum(f.stat().st_size for f in all_md),
            "session_transcripts_count": len(sessions),
            "session_transcripts_size_bytes": sum(f.stat().st_size for f in sessions),
            "feedback_files_count": len(feedbacks),
            "clusters": self._cluster_feedbacks(feedbacks),
        }

    @staticmethod
    def _cluster_feedbacks(feedbacks: list[Path]) -> dict[str, dict[str, Any]]:
        clusters: dict[str, list[str]] = {}
        for f in feedbacks:
            stem = f.stem.removeprefix("feedback_")
            theme = stem.split("_")[0]
            clusters.setdefault(theme, []).append(f.name)
        return {
            theme: {"count": len(files), "files": sorted(files)}
            for theme, files in sorted(clusters.items())
        }


QUICK_FIX_PATTERNS = [
    r"\bfor now\b",
    r"\btemporarily\b",
    r"\bquick fix\b",
    r"\bworkaround\b",
    r"\bhack\b",
    r"\bTODO\b",
    r"\bFIXME\b",
]


@dataclass
class RuleAnalyzer:
    """Analyze CLAUDE.md rule layer."""

    claude_md_path: Path

    def analyze(self) -> dict[str, Any]:
        if not self.claude_md_path.exists():
            return {"claude_md_size_bytes": 0, "claude_md_size_kb": 0,
                    "exceeds_40kb_limit": False, "important_if_blocks": 0,
                    "memory_references": 0, "skill_references": 0,
                    "code_blocks": 0, "quick_fix_pattern_matches": []}

        content = self.claude_md_path.read_text(encoding="utf-8", errors="replace")
        size = self.claude_md_path.stat().st_size

        return {
            "claude_md_size_bytes": size,
            "claude_md_size_kb": (size + 1023) // 1024,
            "exceeds_40kb_limit": size > 40 * 1024,
            "important_if_blocks": len(re.findall(r"<important if", content)),
            "memory_references": len(re.findall(r"feedback_\w+\.md|memory `\w+", content)),
            "skill_references": len(re.findall(r"Skill `\w+|skill `\w+", content)),
            "code_blocks": len(re.findall(r"^```", content, re.MULTILINE)),
            "quick_fix_pattern_matches": self._find_quick_fix_patterns(content),
        }

    @staticmethod
    def _find_quick_fix_patterns(content: str) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for pattern in QUICK_FIX_PATTERNS:
            for m in re.finditer(pattern, content, re.IGNORECASE):
                line_no = content[:m.start()].count("\n") + 1
                matches.append({"pattern": pattern, "line": line_no, "match": m.group()})
        return matches


PLUGIN_LEFTOVER_TAGS = {
    "(gstack)": "gstack",
}

# Skills known to be plugin-distributed (heuristic by skill name + description signal)
KNOWN_PLUGIN_SKILLS = {
    "claude-bug-bounty": "shuvonsec/claude-bug-bounty",
    "ui-ux-pro-max": "nextlevelbuilder/ui-ux-pro-max-skill",
}


@dataclass
class SkillAnalyzer:
    """Analyze skill layer: enumerate ~/.claude/skills/<name>/."""

    skills_dir: Path

    def analyze(self) -> list[dict[str, Any]]:
        if not self.skills_dir.exists():
            return []

        results: list[dict[str, Any]] = []
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            results.append(self._analyze_skill(skill_dir, skill_md))
        return results

    def _analyze_skill(self, skill_dir: Path, skill_md: Path) -> dict[str, Any]:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        refs_dir = skill_dir / "references"
        scripts_dir = skill_dir / "scripts"

        leftover_tag, leftover_plugin = self._detect_plugin_leftover(content, skill_dir.name)

        return {
            "name": skill_dir.name,
            "lines": content.count("\n") + 1,
            "size_bytes": skill_md.stat().st_size,
            "subdirs": sorted([d.name for d in skill_dir.iterdir() if d.is_dir()]),
            "references_count": len(list(refs_dir.glob("*.md"))) if refs_dir.exists() else 0,
            "scripts_count": sum(1 for _ in scripts_dir.glob("*")) if scripts_dir.exists() else 0,
            "inline_code_blocks": len(re.findall(r"^```\w+", content, re.MULTILINE)),
            "is_personal": not bool(leftover_tag),
            "is_plugin_leftover": bool(leftover_tag),
            "leftover_source_plugin": leftover_plugin,
        }

    @staticmethod
    def _detect_plugin_leftover(content: str, skill_name: str) -> tuple[str | None, str | None]:
        for tag, plugin in PLUGIN_LEFTOVER_TAGS.items():
            if tag in content:
                return tag, plugin
        if skill_name in KNOWN_PLUGIN_SKILLS:
            return skill_name, KNOWN_PLUGIN_SKILLS[skill_name]
        return None, None


@dataclass
class PluginAnalyzer:
    """Analyze installed plugins from ~/.claude/plugins/cache/."""

    cache_dir: Path

    def analyze(self) -> list[dict[str, Any]]:
        if not self.cache_dir.exists():
            return []

        results: list[dict[str, Any]] = []
        for marketplace_dir in sorted(self.cache_dir.iterdir()):
            if not marketplace_dir.is_dir() or marketplace_dir.name.startswith("temp_git_"):
                continue
            for plugin_dir in sorted(marketplace_dir.iterdir()):
                if not plugin_dir.is_dir():
                    continue
                versions = sorted([v for v in plugin_dir.iterdir() if v.is_dir()])
                if not versions:
                    continue
                latest = versions[-1]
                results.append(self._analyze_plugin(latest, marketplace_dir.name, plugin_dir.name))
        return results

    def _analyze_plugin(self, version_dir: Path, marketplace: str, plugin: str) -> dict[str, Any]:
        return {
            "name": plugin,
            "marketplace": marketplace,
            "version": version_dir.name,
            "skills_count": len(list(version_dir.glob("**/SKILL.md"))),
            "agents_count": len(list(version_dir.glob("agents/*.md"))),
            "hooks_count": len(list(version_dir.glob("hooks/*"))),
            "commands_count": len(list(version_dir.glob("commands/*.md"))),
        }


@dataclass
class ScriptDetector:
    """Aggregate inline code-block counts across skill .md files."""

    skills_dir: Path

    def analyze(self) -> dict[str, Any]:
        if not self.skills_dir.exists():
            return {"inline_blocks_total": 0, "by_skill": {}}

        by_skill: dict[str, int] = {}
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            count = 0
            for md_file in skill_dir.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8", errors="replace")
                count += len(re.findall(r"^```\w+", content, re.MULTILINE))
            if count > 0:
                by_skill[skill_dir.name] = count

        return {
            "inline_blocks_total": sum(by_skill.values()),
            "by_skill": dict(sorted(by_skill.items(), key=lambda x: -x[1])),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory ~/.claude config artifacts")
    parser.add_argument("--claude-dir", type=Path, default=Path.home() / ".claude",
                        help="Root ~/.claude directory (default: $HOME/.claude)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    inventory = build_inventory(args.claude_dir)
    rendered = json.dumps(inventory, indent=2, default=str)

    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Inventory written: {args.output}")
    else:
        print(rendered)


def _anonymize_path(path: Path) -> str:
    """Replace home prefix with `<home>` placeholder to avoid username leak in public-synced output."""
    home = str(Path.home())
    s = str(path)
    if s.startswith(home):
        return s.replace(home, "<home>", 1)
    return s


def build_inventory(claude_dir: Path) -> dict[str, Any]:
    memory_dir = _select_memory_dir(claude_dir)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claude_dir": _anonymize_path(claude_dir),
        "memory": MemoryAnalyzer(memory_dir).analyze(),
        "rule": RuleAnalyzer(claude_dir / "CLAUDE.md").analyze(),
        "skills": SkillAnalyzer(claude_dir / "skills").analyze(),
        "plugins": PluginAnalyzer(claude_dir / "plugins" / "cache").analyze(),
        "scripts_layer": ScriptDetector(claude_dir / "skills").analyze(),
    }


def _select_memory_dir(claude_dir: Path) -> Path:
    """Pick the memory dir with most *.md files. Fallback ~/.claude/memory if none found."""
    candidates = [p for p in (claude_dir / "projects").glob("*/memory") if p.is_dir()]
    if not candidates:
        return claude_dir / "memory"
    return max(candidates, key=lambda p: len(list(p.glob("*.md"))))


if __name__ == "__main__":
    main()
