from suggestor import Suggestor

def test_suggestor_collects_suggestions():
    detected_structures = [
        {'type': 'List', 'usage_context': 'membership_test', 'line': 2},
        {'type': 'Dictionary', 'usage_context': 'manual_counter', 'line': 4}
    ]
    suggestor = Suggestor(detected_structures)
    suggestions = suggestor.get_suggestions()
    assert len(suggestions) >= 2
