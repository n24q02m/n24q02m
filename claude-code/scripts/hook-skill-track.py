"""PreToolUse hook: log skill invocations."""
import json, sys, os, datetime

try:
    d = json.load(sys.stdin)
    skill = d.get("tool_input", {}).get("skill", "unknown")
    log = os.path.expanduser("~/.claude/skill-usage.log")
    with open(log, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} {skill}\n")
except Exception:
    pass
