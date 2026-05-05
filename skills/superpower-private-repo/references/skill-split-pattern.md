# Skill → Reference Split Pattern (mcp-dev gold standard)

P4 distillation pipeline output. Document khi nào + cách split skill `.md` body → `references/<topic>.md` files.

## Rule of thumb

| SKILL.md lines | Action |
|----------------|--------|
| < 100 | Keep all inline (nothing to split) |
| 100-200 | Inline OK, split if topical coherence allows |
| 200-500 | ⚠ Approaching threshold — split heaviest topical sections |
| > 500 | 🔥 MUST split — heavy skill body breaks lazy-load benefit |

## Gold standard: `mcp-dev`

Current state (2026-05-05): **139 lines SKILL.md + 22 references files**.

Layout pattern:
```
mcp-dev/
├── SKILL.md                          # 139 lines: trigger + scope + invoke conditions + thin pointers per topic
└── references/                       # 22 files lazy-loaded on demand
    ├── audit-commands.md             # Topic 1: gh CLI patterns
    ├── backlog-allowlist.md
    ├── backlog-clearance.md
    ├── clean-state.md
    ├── config-parity.md
    ├── e2e-full-matrix.md
    ├── harness-readiness.md          # Added P5 distillation
    ├── mode-matrix.md
    ├── multi-user-pattern.md
    ├── non-mcp-repos.md
    ├── pr-issue-review.md            # Added P5
    ├── readme-parity.md
    ├── real-plugin-verification.md
    ├── relay-flow.md
    ├── release-cascade.md
    ├── reuse-mcp-core.md
    ├── scope-and-repos.md
    ├── secrets-skret.md
    ├── tool-layout.md
    ├── user-gate-extraction.md       # Added P5
    └── work-order-v3.md              # Added P5
```

**Why gold standard**:
- SKILL.md fits Claude's always-load context (always invoke `Skill mcp-dev` reads ~140 lines)
- Each reference lazy-loaded only when AI follows pointer (Read tool)
- Topics coherent (1 topic per file)
- Names self-documenting (no need to read full content to know what it does)

## Split criteria (when to extract section → reference)

Section qualifies for extraction if ALL true:
1. **Self-contained**: section has clear topic boundary, doesn't depend on context from other sections
2. **>30 lines**: small sections better inline (avoid file-fragmentation)
3. **Optional/conditional**: not always needed — only relevant for specific sub-task
4. **Stable content**: changes <1×/month (frequent-edit content stays inline for lower friction)
5. **Not duplicated elsewhere**: if same content exists in another skill ref → consolidate, don't duplicate

## Extraction workflow

1. Identify section with strong heading (e.g. `## Topic X`)
2. Move section verbatim to `references/<topic-slug>.md` (slug from heading)
3. Replace section in SKILL.md với 1-line pointer: `**See**: \`references/<topic-slug>.md\``
4. Test: ensure SKILL.md still has clear topic flow without extracted section
5. Test: ensure reference file standalone-readable (add brief header context)

## Anti-patterns

- **Don't** split frequently-edited content (each split = extra file to update)
- **Don't** create nested references (`references/<topic>/<subtopic>.md`) — flat is simpler
- **Don't** split by language (e.g. python/`section.md`, sh/`section.md`) — split by topic
- **Don't** split eagerly when SKILL.md < 200 lines (premature optimization)

## When NOT to split

- SKILL.md is process/decision-tree (reading top-to-bottom matters)
- Skill is small (<100 lines) — no benefit
- Topics intermixed (no clear section boundaries) — fix structure first, then split

## Personal kit current state (2026-05-05)

```
ai-ml                            69 lines + 2 refs
error-recurrence-guardrail       61 lines + 0 refs (no split needed)
fullstack-dev                    83 lines + 10 refs (well-split)
infra-devops                     90 lines + 9 refs (well-split)
mcp-dev                         139 lines + 22 refs (gold standard)
product-growth                   38 lines + 4 refs (well-split)
reading-web-exports             104 lines + 0 refs (small, OK)
recurring-task-promoter          45 lines + 0 refs
session-transcript-extraction   283 lines + 0 refs (⚠ candidate for future split)
superpower-private-repo         115 lines + 2 refs (newly added P5 references)
```

0 personal skills exceed 500-line hard threshold currently. Re-audit khi anh add content tới personal skills.

## Memory cross-ref

- `feedback_skill_first_extended.md` — when to invoke skill vs add rule
- Spec section 5 Layer 4 (Reference)
