from clinicops_os.adaptive_memory import (
    MemoryCandidate,
    activation_score,
    decayed_accessibility,
    select_memories,
)


def _candidate(**overrides):
    values = {
        "memory_id": "m1",
        "layer": "L2",
        "topics": ("growth", "eudamed"),
        "utility": 0.9,
        "confidence": 0.9,
        "age_interactions": 10,
        "scope": "internal",
    }
    values.update(overrides)
    return MemoryCandidate(**values)


def test_l1_controls_decay_slower_than_l3_episodes():
    l1 = _candidate(memory_id="control", layer="L1", age_interactions=50)
    l3 = _candidate(memory_id="episode", layer="L3", age_interactions=50)

    assert decayed_accessibility(l1) > decayed_accessibility(l3)


def test_topic_relevance_dominates_irrelevant_memory():
    relevant = _candidate(memory_id="relevant", topics=("growth", "eudamed"))
    irrelevant = _candidate(memory_id="irrelevant", topics=("billing", "payroll"))

    assert activation_score(relevant, ("growth", "eudamed")) > activation_score(
        irrelevant, ("growth", "eudamed")
    )


def test_uncertainty_increases_value_of_deeper_evidence():
    episode = _candidate(memory_id="episode", layer="L3")

    certain = activation_score(episode, ("growth",), uncertainty=0.0)
    uncertain = activation_score(episode, ("growth",), uncertainty=1.0)

    assert uncertain > certain


def test_private_memory_is_fail_closed_by_default():
    private = _candidate(memory_id="private", scope="private")
    internal = _candidate(memory_id="internal", scope="internal")

    selected = select_memories([private, internal], ("growth",), threshold=0.0)

    assert [item.memory_id for item in selected] == ["internal"]


def test_private_memory_requires_explicit_scope_permission():
    private = _candidate(memory_id="private", scope="private")

    selected = select_memories(
        [private],
        ("growth",),
        allowed_scopes=frozenset({"private"}),
        threshold=0.0,
    )

    assert [item.memory_id for item in selected] == ["private"]


def test_selector_respects_max_items_and_score_order():
    high = _candidate(memory_id="high", utility=1.0, confidence=1.0, age_interactions=0)
    medium = _candidate(memory_id="medium", utility=0.8, confidence=0.8, age_interactions=3)
    low = _candidate(memory_id="low", utility=0.4, confidence=0.4, age_interactions=20)

    selected = select_memories(
        [low, medium, high],
        ("growth",),
        threshold=0.0,
        max_items=2,
    )

    assert [item.memory_id for item in selected] == ["high", "medium"]
