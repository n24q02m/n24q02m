"""Error ledger for error-recurrence-guardrail skill.

Normalize + hash + increment counter for recurring errors; emit proposals
when count crosses threshold_m.
"""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List


_PATH_RE = re.compile(r'(/[\w./\-]+|[A-Z]:[\\/][\w.\\/\-]+)')
_TS_RE = re.compile(
    r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+\-]\d{2}:\d{2})?'
)
_LINE_RE = re.compile(r'\bline \d+\b|\bat line \d+\b', re.IGNORECASE)
_PID_RE = re.compile(r'\bpid[=: ]\d+\b', re.IGNORECASE)


def normalize_error(raw: str) -> str:
    """Strip volatile tokens (paths, timestamps, line numbers, PIDs) for stable signature.

    Order matters: timestamps first (otherwise path regex eats `2026-04-17T10` part).
    """
    s = _TS_RE.sub("<ts>", raw)
    s = _PATH_RE.sub("<path>", s)
    s = _LINE_RE.sub("<line>", s)
    s = _PID_RE.sub("<pid>", s)
    return s.strip()


def signature(normalized: str) -> str:
    """Stable 16-char sha256 prefix of normalized error."""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


class ErrorLedger:
    """Append-read-update JSONL ledger for recurring error detection."""

    def __init__(self, path: Path | str, threshold_m: int = 2) -> None:
        self.path = Path(path)
        self.threshold_m = threshold_m
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def read_all(self) -> List[dict]:
        content = self.path.read_text(encoding="utf-8")
        return [json.loads(l) for l in content.splitlines() if l.strip()]

    def _write_all(self, entries: List[dict]) -> None:
        body = "\n".join(json.dumps(e, ensure_ascii=False) for e in entries)
        self.path.write_text(body + ("\n" if body else ""), encoding="utf-8")

    def record(self, raw_error: str, session: str) -> List[dict]:
        """Record error. Returns list of triggered proposals (empty if below threshold)."""
        normalized = normalize_error(raw_error)
        sig = signature(normalized)
        entries = self.read_all()
        proposals: List[dict] = []
        updated = False

        for e in entries:
            if e["error_signature"] == sig:
                e["count"] += 1
                e.setdefault("sessions", []).append(session)
                e["ts"] = datetime.now(timezone.utc).isoformat()
                if e["count"] >= self.threshold_m and e["status"] == "pending":
                    proposals.append(dict(e))
                updated = True
                break

        if not updated:
            entries.append({
                "ts": datetime.now(timezone.utc).isoformat(),
                "error_signature": sig,
                "normalized": normalized,
                "count": 1,
                "sessions": [session],
                "root_cause_guess": "",
                "proposed_rule": "",
                "status": "pending",
            })

        self._write_all(entries)
        return proposals
