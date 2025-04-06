from rules import rules

def test_membership_test_rule_trigger():
    structure = {'type': 'List', 'usage_context': 'membership_test'}
    rule = rules[0]  # membership test rule
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'Use a set' in suggestion['suggestion']

def test_manual_counter_rule_trigger():
    structure = {'type': 'Dictionary', 'usage_context': 'manual_counter'}
    rule = rules[1]  # manual counter rule
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'collections.Counter' in suggestion['suggestion']

def test_queue_like_usage_rule_trigger():
    structure = {'type': 'List', 'usage_context': 'append_or_pop'}
    rule = rules[2]  # deque suggestion rule
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'deque' in suggestion['suggestion']
