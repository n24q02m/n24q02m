"""Stop hook: send Telegram notification when session ends."""
import json, sys, os, urllib.request

try:
    d = json.load(sys.stdin)
    token = os.environ.get("VC_SECRETARY_BOT_TOKEN", "")
    chat = os.environ.get("VC_OWNER_CHAT_ID", "7305908576")
    if not token:
        sys.exit(0)
    sid = str(d.get("session_id", "unknown"))[:8]
    msg = f"Claude Code session ended: {sid}"
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat, "text": msg}).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=5)
except Exception:
    pass
