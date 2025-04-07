from rules import rules
from rules import is_membership_test_on_list


def test_membership_test_rule_trigger():
    structure = {
        "line": 4,
        "type": "Membership Test on data",
        "usage_context": "membership_test",
        "details": "Membership test detected (consider using set)."
    }
    assert is_membership_test_on_list(structure)



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
