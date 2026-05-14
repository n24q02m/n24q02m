# Claude Code Authoring (Hooks / Skills / Plugins)

Distilled from `plugin-dev` + `hookify` plugins (dropped 2026-05-09). Captures novel patterns not in CLAUDE.md or other refs. For full reference: official docs https://docs.claude.com/en/docs/claude-code/hooks + https://docs.claude.com/en/docs/claude-code/sub-agents.

## 1. Hook events (full table)

| Event | Fires when | Use for | Decision-capable |
|---|---|---|---|
| `PreToolUse` | Before any tool runs | Validate / approve / deny / modify tool calls | Yes (allow/deny/ask) |
| `PostToolUse` | After tool completes | React to results, feedback to Claude | No (advisory only) |
| `Stop` | Main agent considers stopping | Completion checks, enforce checklist | Yes (approve/block) |
| `SubagentStop` | Subagent considers stopping | Validate subagent task | Yes (approve/block) |
| `UserPromptSubmit` | User submits prompt | Add context, validate, block | Yes (block) |
| `SessionStart` | Session begins | Load project context, set env vars | No |
| `SessionEnd` | Session ends | Cleanup, logging, state preservation | No |
| `PreCompact` | Before context compaction | Preserve critical info | No |
| `Notification` | User notified | Logging, reactions | No |

## 2. Hook config formats — TWO different shapes

### Plugin (`hooks/hooks.json`) — wrapper format
```json
{
  "description": "optional",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "prompt", "prompt": "...", "timeout": 30 }
        ]
      }
    ]
  }
}
```

### User settings (`~/.claude/settings.json`) — direct format (no wrapper)
```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

Critical: plugin format wraps events in `{"hooks": {...}}`; settings format puts events directly under `"hooks"` key. Easy to mix up.

## 3. Hook types

### Prompt-based (LLM decides) — preferred for context-aware logic
```json
{
  "type": "prompt",
  "prompt": "Validate file write safety. Check: system paths, credentials, path traversal. Return 'approve' or 'deny'.",
  "timeout": 30
}
```
Supported events: `Stop`, `SubagentStop`, `UserPromptSubmit`, `PreToolUse`. Default timeout 30s.

### Command-based (deterministic shell) — preferred for fast/precise checks
```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 60
}
```
Default timeout 60s. Always use `${CLAUDE_PLUGIN_ROOT}` for portability.

## 4. Matchers (regex against tool name)

```json
"matcher": "Write"                    // exact
"matcher": "Read|Write|Edit"          // multiple (OR)
"matcher": "*"                        // all tools
"matcher": "mcp__.*"                  // all MCP tools
"matcher": "mcp__plugin_asana_.*"     // specific plugin's tools
"matcher": "mcp__.*__delete.*"        // pattern across plugins
"matcher": "Bash"                     // bash only
```

Case-sensitive. Empty `""` = match nothing (settings example uses for PostToolUse "all tools").

## 5. Hook input (via stdin JSON)

Common fields all hooks receive:
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "PreToolUse"
}
```

Event-specific:
- `PreToolUse` / `PostToolUse`: `tool_name`, `tool_input`, `tool_result`
- `UserPromptSubmit`: `user_prompt`
- `Stop` / `SubagentStop`: `reason`

In prompt-based hooks: access via `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`.

## 6. Hook output (stdout JSON)

### PreToolUse (decision)
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": { "field": "modified_value" }
  },
  "systemMessage": "Explanation for Claude"
}
```

### Stop / SubagentStop (decision)
```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

### Generic (all hooks)
```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

Exit codes: `0` = success (stdout shown), `2` = blocking error (stderr fed back), other = non-blocking error.

## 7. Environment vars (command hooks only)

- `$CLAUDE_PROJECT_DIR` — project root
- `$CLAUDE_PLUGIN_ROOT` — plugin dir (use for portable script paths)
- `$CLAUDE_ENV_FILE` — **SessionStart only**: persist env vars by appending `export FOO=bar` to this path
- `$CLAUDE_CODE_REMOTE` — set if running remotely

## 8. Parallel execution (gotcha)

All matching hooks for an event run in **parallel**, not in declaration order. Implications:
- Hooks DON'T see each other's output
- Order is non-deterministic
- Design hooks to be independent
- Don't mutate global state

## 9. Hot-reload limitation

Hooks load at session start. **Editing `hooks.json` does NOT affect current session** — must restart Claude Code (`/exit` then `claude`). Use `claude --debug` for hook execution logs. `/hooks` command shows currently loaded hooks.

## 10. Hookify-equivalent (regex pattern watcher) without the plugin

Hookify provides a markdown frontmatter abstraction over PreToolUse hooks. To replicate without the plugin, write a thin Python/Bash script:

```python
#!/usr/bin/env python3
# ~/.claude/scripts/hook-pattern-watcher.py
import json, re, sys
data = json.load(sys.stdin)
tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

DANGEROUS_PATTERNS = [
    (r'rm\s+-rf', "rm -rf detected — confirm before execution"),
    (r'console\.log\(', "console.log added — remove before commit"),
    (r'\.env\s*$', "editing .env file — verify gitignore"),
]

if tool_name == "Bash":
    cmd = tool_input.get("command", "")
    for pat, msg in DANGEROUS_PATTERNS:
        if re.search(pat, cmd):
            print(json.dumps({"systemMessage": msg}))
            sys.exit(0)
elif tool_name in ("Edit", "Write", "MultiEdit"):
    text = tool_input.get("new_text", "") + tool_input.get("content", "")
    path = tool_input.get("file_path", "")
    for pat, msg in DANGEROUS_PATTERNS:
        if re.search(pat, text) or re.search(pat, path):
            print(json.dumps({"systemMessage": msg}))
            sys.exit(0)
sys.exit(0)
```

Wire in `~/.claude/settings.json`:
```json
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash|Edit|Write|MultiEdit",
    "hooks": [{ "type": "command", "command": "python3 ~/.claude/scripts/hook-pattern-watcher.py" }]
  }]
}
```

Hookify benefits not replicated: per-rule .md files, hot-load (changes ed take effect next tool use). For most use cases, hardcoded patterns in 1 script is enough.

## 11. SKILL.md authoring (when writing personal skills)

```markdown
---
name: skill-name (kebab-case)
description: One sentence. CC matches this against user intent for auto-invoke. Be specific.
---

# Skill Name

## When to use
- Trigger condition 1
- Trigger condition 2

## What this skill enforces
[Body content — invoked when relevant]

## References (doc on demand)
- `references/topic-1.md` — purpose
- `references/topic-2.md` — purpose
```

Progressive disclosure: only `description` always loaded; full body + references read on-demand. Keep body lean (<10KB). Move heavy content to `references/*.md` files.

Rule of thumb (from CLAUDE.md feedback): **CLAUDE.md rule = thin trigger + pointer**, full content lives in skill body or references.

## 12. Plugin structure (when scaffolding new plugin)

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # name, version, description, author
├── README.md
├── skills/                   # optional
│   └── skill-name/
│       └── SKILL.md
├── commands/                 # optional slash commands
│   └── command-name.md       # YAML frontmatter + body
├── agents/                   # optional subagents
│   └── agent-name.md
├── hooks/                    # optional
│   └── hooks.json            # plugin format (with "hooks" wrapper)
├── .mcp.json                 # optional MCP server registration
└── examples/                 # optional usage examples
```

`plugin.json` minimum:
```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "What this plugin does",
  "author": { "name": "...", "email": "..." }
}
```

Marketplace: register in `marketplace.json` at root of marketplace repo. Plugin source can be `github`, `git`, or `local`.

## 13. Slash command (.md) frontmatter

```markdown
---
name: my-command
description: What this command does
---

Body becomes the prompt sent to Claude when /my-command invoked.
Can include $ARGUMENTS to insert user-provided args.
```

## 14. Subagent (.md) frontmatter

```markdown
---
name: my-agent
description: When to invoke this agent (Claude reads this for routing)
tools: ["Read", "Edit", "Bash"]   # optional whitelist
---

System prompt for the agent. Should describe:
- The task it's specialized in
- Constraints / patterns to follow
- Output format expected
```

## 15. Debugging

- `claude --debug` — full hook + plugin lifecycle logs
- `/hooks` — list currently loaded hooks
- `/plugin` — list installed plugins, enable/disable
- `/doctor` — diagnostic + skill listing budget warning
- Test command hook directly: `echo '{"tool_name":"Write","tool_input":{...}}' | bash hook.sh`
- Validate JSON output: pipe through `jq .`

## 16. Security checklist (command hooks)

- `set -euo pipefail` at top
- Quote all variables: `"$file_path"`, never `$file_path`
- Validate inputs (regex check tool_name format)
- Reject path traversal: check `*".."*`
- Set timeout (default 60s for command, 30s for prompt)
- Don't log secrets to stdout (gets shown in transcript)
- Use `${CLAUDE_PLUGIN_ROOT}` not hardcoded paths

---

**Storage convention**: This file lives in `~/.claude/skills/infra-devops/references/` and is read on-demand when authoring hooks/skills/plugins. Don't duplicate in CLAUDE.md (CLAUDE.md = thin trigger + pointer pattern).
