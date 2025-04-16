# test_suggestor.py

from suggestor import Suggestor

# Test that Suggestor correctly collects suggestions for multiple structures
def test_suggestor_collects_suggestions():
    # Simulated structures that should trigger two distinct suggestions
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

    # Expect at least 2 suggestions, one per structure
    assert len(suggestions) >= 2

# Test that the snippet generator correctly attaches fix suggestions for known patterns
def test_snippet_generator_adds_correct_snippet():
    # Simulated structures for three different rule types
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

    # Validate that at least one fix snippet references each expected structure
    assert any("Counter" in s["fix_snippet"] for s in suggestions)
    assert any("set" in s["fix_snippet"] for s in suggestions)
    assert any("deque" in s["fix_snippet"] for s in suggestions)
