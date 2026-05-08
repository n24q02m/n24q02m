"""Cluster recurring action tuples from session transcripts.

Used by recurring-task-promoter skill to detect tasks user has requested >=N times
and propose automation (new skill, CLAUDE.md rule).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ActionTuple:
    verb: str
    target: str
    session: str


@dataclass
class Cluster:
    verb: str
    target: str
    sessions: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.sessions)


@dataclass
class Proposal:
    summary: str
    evidence: List[str]


def cluster_actions(
    tuples: List[ActionTuple],
    threshold_similarity: float = 0.8,
) -> List[Cluster]:
    """Group action tuples by (verb_lower, target_lower).

    threshold_similarity reserved for future semantic clustering (v0.2+).
    """
    grouped: dict[tuple[str, str], Cluster] = {}
    for t in tuples:
        key = (t.verb.lower().strip(), t.target.lower().strip())
        if key not in grouped:
            grouped[key] = Cluster(verb=t.verb, target=t.target)
        grouped[key].sessions.append(t.session)
    return list(grouped.values())


def propose_promotions(clusters: List[Cluster], threshold_n: int = 3) -> List[Proposal]:
    """Return proposals for clusters meeting threshold count."""
    out: List[Proposal] = []
    for c in clusters:
        if c.count >= threshold_n:
            out.append(Proposal(
                summary=f"{c.verb} {c.target}",
                evidence=list(c.sessions),
            ))
    return out
