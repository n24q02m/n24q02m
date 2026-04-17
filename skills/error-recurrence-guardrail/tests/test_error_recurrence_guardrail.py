"""Tests for error-recurrence-guardrail ledger logic."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from error_ledger import ErrorLedger, normalize_error, signature


def test_normalize_strips_paths_timestamps() -> None:
    raw = "FileNotFoundError: /tmp/abc-2026-04-17T10:30:00/file.txt at line 123"
    norm = normalize_error(raw)
    assert "2026-04-17" not in norm
    assert "/tmp/abc" not in norm
    assert "line 123" not in norm
    assert "FileNotFoundError" in norm
    assert "<path>" in norm
    assert "<ts>" in norm
    assert "<line>" in norm


def test_signature_stable() -> None:
    assert signature("ModuleNotFoundError: foo") == signature("ModuleNotFoundError: foo")
    assert signature("A") != signature("B")
    # Same input always produces same hash
    assert len(signature("any")) == 16


def test_ledger_increment(tmp_path) -> None:
    p = tmp_path / "ledger.jsonl"
    led = ErrorLedger(p)
    proposals_first = led.record("ModuleNotFoundError: foo", session="s1")
    assert proposals_first == []  # first time, below threshold
    proposals_second = led.record("ModuleNotFoundError: foo", session="s2")
    assert len(proposals_second) == 1  # crosses threshold_m=2
    entries = led.read_all()
    assert len(entries) == 1
    assert entries[0]["count"] == 2
    assert entries[0]["sessions"] == ["s1", "s2"]


def test_threshold_triggers_proposal(tmp_path) -> None:
    p = tmp_path / "ledger.jsonl"
    led = ErrorLedger(p, threshold_m=2)
    led.record("AttributeError: NoneType has no attribute foo", session="s1")
    proposals = led.record("AttributeError: NoneType has no attribute foo", session="s2")
    assert len(proposals) == 1
    assert "AttributeError" in proposals[0]["normalized"]
    assert proposals[0]["sessions"] == ["s1", "s2"]


def test_different_errors_separate_entries(tmp_path) -> None:
    p = tmp_path / "ledger.jsonl"
    led = ErrorLedger(p)
    led.record("ErrorA", session="s1")
    led.record("ErrorB", session="s1")
    entries = led.read_all()
    assert len(entries) == 2


def test_path_normalization_same_signature(tmp_path) -> None:
    p = tmp_path / "ledger.jsonl"
    led = ErrorLedger(p)
    # Same error with different paths should get same signature
    led.record("FileNotFoundError: /tmp/run-1/file.txt at line 10", session="s1")
    proposals = led.record("FileNotFoundError: /var/tmp/run-2/file.txt at line 42", session="s2")
    assert len(proposals) == 1
    entries = led.read_all()
    assert len(entries) == 1
    assert entries[0]["count"] == 2
