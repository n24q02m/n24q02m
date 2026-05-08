"""Tests for extract_inline_scripts.py — uses tmp_path fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest

from extract_inline_scripts import LANG_TO_EXT, CODE_BLOCK_RE


def test_lang_extension_map() -> None:
    assert LANG_TO_EXT["bash"] == ".sh"
    assert LANG_TO_EXT["python"] == ".py"
    assert LANG_TO_EXT["typescript"] == ".ts"


def test_code_block_regex_matches_simple() -> None:
    md = "Some text\n```bash\necho hello\n```\nMore text"
    matches = list(CODE_BLOCK_RE.finditer(md))
    assert len(matches) == 1
    assert matches[0].group(1) == "bash"
    assert matches[0].group(2) == "echo hello\n"


from extract_inline_scripts import extract_skill, ExtractedBlock


def test_extract_skill_creates_scripts_and_replaces_blocks(tmp_path: Path) -> None:
    skill = tmp_path / "my-skill"
    skill.mkdir()
    skill_md = skill / "SKILL.md"
    skill_md.write_text("""---
name: my-skill
---

# My Skill

Run this:

```bash
echo first
ls /tmp
```

And then:

```python
import os
print(os.getcwd())
```

Done.
""", encoding="utf-8")

    blocks = extract_skill(skill)

    # Two blocks extracted
    assert len(blocks) == 2
    assert blocks[0].lang == "bash"
    assert blocks[1].lang == "python"

    # Scripts created
    scripts_dir = skill / "scripts"
    assert (scripts_dir / "skill-1.sh").exists()
    assert (scripts_dir / "skill-2.py").exists()
    assert "echo first" in (scripts_dir / "skill-1.sh").read_text()
    assert "import os" in (scripts_dir / "skill-2.py").read_text()

    # SKILL.md updated with pointers
    new_content = skill_md.read_text(encoding="utf-8")
    assert "```bash" not in new_content
    assert "```python" not in new_content
    assert "scripts/skill-1.sh" in new_content
    assert "scripts/skill-2.py" in new_content


def test_extract_skill_handles_references_dir(tmp_path: Path) -> None:
    skill = tmp_path / "my-skill"
    refs = skill / "references"
    refs.mkdir(parents=True)
    ref_md = refs / "topic-a.md"
    ref_md.write_text("```sh\nfoo\n```", encoding="utf-8")

    blocks = extract_skill(skill)

    assert len(blocks) == 1
    # Script lives at skill/scripts/, not skill/references/scripts/
    assert (skill / "scripts" / "topic-a-1.sh").exists()
    # Reference .md updated
    new_content = ref_md.read_text(encoding="utf-8")
    assert "```sh" not in new_content
    assert "scripts/topic-a-1.sh" in new_content


def test_extract_skill_dry_run_does_not_modify(tmp_path: Path) -> None:
    skill = tmp_path / "my-skill"
    skill.mkdir()
    skill_md = skill / "SKILL.md"
    original = "```bash\necho x\n```"
    skill_md.write_text(original, encoding="utf-8")

    blocks = extract_skill(skill, dry_run=True)

    assert len(blocks) == 1
    assert skill_md.read_text(encoding="utf-8") == original
    assert not (skill / "scripts").exists()


def test_extract_skill_idempotent(tmp_path: Path) -> None:
    skill = tmp_path / "my-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("```bash\necho x\n```", encoding="utf-8")

    first = extract_skill(skill)
    assert len(first) == 1

    # Second run: no inline blocks remain, should extract 0
    second = extract_skill(skill)
    assert len(second) == 0


def test_extract_skill_skips_unknown_lang(tmp_path: Path) -> None:
    skill = tmp_path / "my-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "```yaml\nkey: value\n```\n```bash\necho x\n```",
        encoding="utf-8"
    )

    blocks = extract_skill(skill)
    # Only bash extracted (yaml skipped)
    assert len(blocks) == 1
    assert blocks[0].lang == "bash"
    # yaml block still in .md
    assert "```yaml" in (skill / "SKILL.md").read_text(encoding="utf-8")
