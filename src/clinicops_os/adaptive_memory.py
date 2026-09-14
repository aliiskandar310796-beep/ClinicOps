"""Deterministic, evidence-aware memory routing for ClinicOps agents.

This module implements a small original policy inspired by the general idea of
hierarchical, decay-driven memory activation. It does not depend on or copy an
external memory framework.

ClinicOps uses three memory layers:

* L1 — durable controls and strategy (claim rules, shared agent state).
* L2 — time-bounded semantic facts and validated research claims.
* L3 — episodic operational evidence (buyer interactions, runs, failures).

Decay only changes retrieval priority. It never deletes evidence. Private
memories are fail-closed unless the caller explicitly permits private scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Iterable, Literal, Sequence

MemoryLayer = Literal["L1", "L2", "L3"]
MemoryScope = Literal["public", "internal", "private"]

_LAYER_RETENTION = {"L1": 4.0, "L2": 1.6, "L3": 0.8}
_LAYER_DEPTH_BOOST = {"L1": 0.00, "L2": 0.06, "L3": 0.12}


@dataclass(frozen=True)
class MemoryCandidate:
    """A memory item eligible for deterministic activation scoring."""

    memory_id: str
    layer: MemoryLayer
    topics: tuple[str, ...]
    utility: float
    confidence: float
    age_interactions: int = 0
    scope: MemoryScope = "internal"

    def __post_init__(self) -> None:
        if not self.memory_id.strip():
            raise ValueError("memory_id must be non-empty")
        if self.layer not in _LAYER_RETENTION:
            raise ValueError(f"unsupported layer: {self.layer}")
        if not 0 <= self.utility <= 1:
            raise ValueError("utility must be between 0 and 1")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.age_interactions < 0:
            raise ValueError("age_interactions must be non-negative")


def _normalize_topics(topics: Iterable[str]) -> set[str]:
    return {topic.strip().lower() for topic in topics if topic.strip()}


def topic_match(candidate: MemoryCandidate, task_topics: Iterable[str]) -> float:
    """Return a 0..1 topic-overlap score."""

    memory_topics = _normalize_topics(candidate.topics)
    requested = _normalize_topics(task_topics)
    if not memory_topics or not requested:
        return 0.0
    return len(memory_topics & requested) / len(requested)


def decayed_accessibility(
    candidate: MemoryCandidate,
    *,
    decay_rate: float = 0.06,
) -> float:
    """Return accessibility after interaction-based decay.

    L1 decays slowest and L3 fastest. The result remains in 0..1.
    """

    if decay_rate < 0:
        raise ValueError("decay_rate must be non-negative")
    retention = _LAYER_RETENTION[candidate.layer]
    decay = exp(-(decay_rate * candidate.age_interactions) / retention)
    return candidate.utility * candidate.confidence * decay


def activation_score(
    candidate: MemoryCandidate,
    task_topics: Iterable[str],
    *,
    uncertainty: float = 0.0,
    decay_rate: float = 0.06,
) -> float:
    """Score a memory for activation.

    Higher uncertainty slightly favors deeper evidence layers, while topic
    relevance remains the dominant signal. The score is clipped to 0..1.
    """

    if not 0 <= uncertainty <= 1:
        raise ValueError("uncertainty must be between 0 and 1")

    relevance = topic_match(candidate, task_topics)
    accessibility = decayed_accessibility(candidate, decay_rate=decay_rate)
    depth_boost = uncertainty * _LAYER_DEPTH_BOOST[candidate.layer]

    score = (0.50 * relevance) + (0.40 * accessibility) + depth_boost
    return min(1.0, max(0.0, score))


def select_memories(
    candidates: Sequence[MemoryCandidate],
    task_topics: Iterable[str],
    *,
    uncertainty: float = 0.0,
    allowed_scopes: frozenset[MemoryScope] = frozenset({"public", "internal"}),
    threshold: float = 0.28,
    max_items: int = 8,
    decay_rate: float = 0.06,
) -> list[MemoryCandidate]:
    """Select and rank memories that should enter working context.

    Private memories are excluded unless ``private`` is present in
    ``allowed_scopes``. This is intentional: retrieving deep operational
    history must be an explicit decision, not a side effect of broad search.
    """

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if max_items < 1:
        raise ValueError("max_items must be at least 1")

    scored: list[tuple[float, MemoryCandidate]] = []
    for candidate in candidates:
        if candidate.scope not in allowed_scopes:
            continue
        score = activation_score(
            candidate,
            task_topics,
            uncertainty=uncertainty,
            decay_rate=decay_rate,
        )
        if score >= threshold:
            scored.append((score, candidate))

    scored.sort(
        key=lambda item: (
            item[0],
            item[1].confidence,
            item[1].utility,
            -item[1].age_interactions,
            item[1].memory_id,
        ),
        reverse=True,
    )
    return [candidate for _, candidate in scored[:max_items]]
