"""Tests for recurring-task-promoter clustering logic."""
import sys
from pathlib import Path

# allow running from skill root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cluster_tasks import ActionTuple, cluster_actions, propose_promotions


def test_cluster_actions_basic() -> None:
    tuples = [
        ActionTuple(verb="read", target="screenshot", session="s1"),
        ActionTuple(verb="read", target="screenshot", session="s2"),
        ActionTuple(verb="read", target="screenshot", session="s3"),
        ActionTuple(verb="update", target="spec", session="s1"),
    ]
    clusters = cluster_actions(tuples)
    assert len(clusters) == 2
    read_cluster = next(c for c in clusters if c.verb == "read")
    assert read_cluster.count == 3
    update_cluster = next(c for c in clusters if c.verb == "update")
    assert update_cluster.count == 1


def test_case_insensitive_cluster() -> None:
    tuples = [
        ActionTuple(verb="Read", target="Screenshot", session="s1"),
        ActionTuple(verb="READ", target="screenshot", session="s2"),
    ]
    clusters = cluster_actions(tuples)
    assert len(clusters) == 1
    assert clusters[0].count == 2


def test_propose_promotions_threshold() -> None:
    tuples = [
        ActionTuple(verb="read", target="screenshot", session=f"s{i}")
        for i in range(3)
    ]
    clusters = cluster_actions(tuples)
    proposals = propose_promotions(clusters, threshold_n=3)
    assert len(proposals) == 1
    assert "read screenshot" in proposals[0].summary
    assert proposals[0].evidence == ["s0", "s1", "s2"]


def test_propose_promotions_below_threshold() -> None:
    tuples = [
        ActionTuple(verb="read", target="screenshot", session="s1"),
        ActionTuple(verb="read", target="screenshot", session="s2"),
    ]
    clusters = cluster_actions(tuples)
    proposals = propose_promotions(clusters, threshold_n=3)
    assert proposals == []
