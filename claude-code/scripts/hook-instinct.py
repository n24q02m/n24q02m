"""PostToolUse hook: log tool usage patterns for instinct extraction."""
import json, sys, os, datetime

try:
    d = json.load(sys.stdin)
    tool = d.get("tool_name", "")
    log = os.path.expanduser("~/.claude/instinct.log")
    with open(log, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} {tool}\n")
except Exception:
    pass
