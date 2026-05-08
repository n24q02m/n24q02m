# `~/.claude/scripts/`

Scripts hỗ trợ distillation pipeline (spec: `.superpower/n24q02m/specs/2026-05-05-claude-config-distillation-pipeline-design.md`).

## `distill-inventory.{py,sh}`

Inventory tool — enumerate artifact trong `~/.claude/` config + xuất JSON.

### Usage

```bash
# Run + print JSON to stdout
./distill-inventory.sh

# Save to file
./distill-inventory.sh --output /tmp/inventory.json

# Custom claude dir
./distill-inventory.sh --claude-dir /path/to/claude
```

### Output schema (top-level keys)

- `schema_version`: "1.0"
- `generated_at`: ISO8601 UTC timestamp
- `claude_dir`: absolute path scanned
- `memory`: `{total_files, total_size_bytes, session_transcripts_count, feedback_files_count, clusters}`
- `rule`: `{claude_md_size_bytes, claude_md_size_kb, exceeds_40kb_limit, important_if_blocks, memory_references, skill_references, code_blocks, quick_fix_pattern_matches}`
- `skills`: list of `{name, lines, references_count, scripts_count, inline_code_blocks, is_personal, is_plugin_leftover, leftover_source_plugin}`
- `plugins`: list of `{name, marketplace, version, skills_count, agents_count, hooks_count, commands_count}`
- `scripts_layer`: `{inline_blocks_total, by_skill}`

### Tests

```bash
python -m pytest test_distill_inventory.py -v
```

### Tech

- Python 3.13 stdlib only (pathlib, json, re, argparse, dataclasses)
- 0 external deps
- Cross-platform (Windows/Mac/Linux)

### Used by phases

- P2 script extraction: `scripts_layer.by_skill` to prioritize targets
- P3 memory pruning: `memory.clusters` for cluster consolidation; `memory.session_transcripts_count` for archive
- P4 skill→ref split: `skills[].lines >= 500` triggers split eligibility
- P5 rule cleanup: `rule.exceeds_40kb_limit` + `rule.quick_fix_pattern_matches` for audit
- P7 plugin curation: `skills[].is_plugin_leftover` for cleanup; `plugins[]` for verify endstate
