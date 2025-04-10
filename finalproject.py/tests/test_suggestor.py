from suggestor import Suggestor

def test_suggestor_collects_suggestions():
    structures = [
        {
            "line": 2,
            "type": "Membership Test on data",
            "usage_context": "membership_test",
            "details": "Membership test detected (consider using set)."
        },
        {
            "line": 4,
            "type": "Dictionary",
            "usage_context": "manual_counter",
            "details": "Manual counter pattern (dict.get + 1)."
        }
    ]

    suggestor = Suggestor(structures)
    suggestions = suggestor.get_suggestions()

    assert len(suggestions) >= 2


def test_snippet_generator_adds_correct_snippet():
    structures = [
        {
            "line": 5,
            "type": "Dictionary",
            "usage_context": "manual_counter",
            "details": "Manual counter pattern (dict.get + 1)."
        },
        {
            "line": 10,
            "type": "Membership Test on data",
            "usage_context": "membership_test",
            "details": "Membership test detected (consider using set)."
        },
        {
            "line": 15,
            "type": "List",
            "usage_context": "append_or_pop",
            "details": "append usage detected (may indicate inefficient queue use)."
        }
    ]

    suggestor = Suggestor(structures)
    suggestions = suggestor.get_suggestions()

    assert any("Counter" in s["fix_snippet"] for s in suggestions)
    assert any("set" in s["fix_snippet"] for s in suggestions)
    assert any("deque" in s["fix_snippet"] for s in suggestions)
