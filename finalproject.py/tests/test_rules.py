from rules import rules
from rules import (
    is_membership_test_on_list,
    is_manual_counter_detected,
    is_queue_like_list_usage,
    is_dict_keys_loop,
    is_redundant_conversion,
    is_manual_dict_loop,
    is_reversed_temp_list,
    is_ordereddict_used_like_dict,
)

# Test that a membership test on a list triggers the rule
def test_membership_test_rule_trigger():
    structure = {
        "line": 4,
        "type": "Membership Test on data",
        "usage_context": "membership_test",
        "details": "Membership test detected (consider using set)."
    }
    assert is_membership_test_on_list(structure)

# Test that a manual counter pattern suggests using collections.Counter
def test_manual_counter_rule_trigger():
    structure = {'type': 'Dictionary', 'usage_context': 'manual_counter'}
    rule = rules[1]  # manual counter rule
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'collections.Counter' in suggestion['suggestion']

# Test that list-based queue operations suggest using deque
def test_queue_like_usage_rule_trigger():
    structure = {'type': 'List', 'usage_context': 'append_or_pop'}
    rule = rules[2]  # deque suggestion rule
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'deque' in suggestion['suggestion']

# Test that iterating over dict.keys() suggests direct iteration over the dictionary
def test_dict_keys_loop_rule_trigger():
    structure = {
        "line": 10,
        "type": "Dictionary Iteration",
        "usage_context": "dict_keys_loop",
        "details": "Iteration over dict.keys() detected."
    }
    rule = rules[3]
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'iterate directly' in suggestion['suggestion'].lower()

# Test that redundant list(set(...)) or set(list(...)) is flagged
def test_redundant_conversion_rule_trigger():
    structure = {
        "line": 8,
        "type": "Redundant Conversion",
        "usage_context": "redundant_conversion",
        "details": "list(set(...)) detected — may be redundant."
    }
    rule = rules[4]
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'redundant' in suggestion['suggestion'].lower()

# Test that manual dictionary construction inside a loop is flagged
def test_manual_dict_loop_rule_trigger():
    structure = {
        "line": 6,
        "type": "Manual Dict Construction",
        "usage_context": "manual_dict_loop",
        "details": "Manual dict built via loop to `d`."
    }
    rule = rules[5]
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'dict(zip' in suggestion['suggestion'].lower() or 'comprehension' in suggestion['suggestion'].lower()

# Test that reversing a temporary list is flagged as inefficient
def test_reversed_temp_list_rule_trigger():
    structure = {
        "line": 7,
        "type": "Reversed List",
        "usage_context": "reversed_temp_list",
        "details": "reversed(list(...)) detected — creates unnecessary temporary list."
    }
    rule = rules[6]
    suggestion = rule.apply(structure)
    assert suggestion is not None
    assert 'reversing a temporary list' in suggestion['suggestion'].lower() or 'reversed()' in suggestion['suggestion'].lower()

# Test that using OrderedDict without special behaviour triggers a suggestion to use dict
def test_ordereddict_used_like_dict_rule_trigger():
    structure = {
        "type": "OrderedDict",
        "details": "Preserves insertion order (collections.OrderedDict)."
        # No usage_context included — matches rule condition
    }
    suggestion = rules[7].apply(structure)
    assert suggestion is not None
    assert "dict" in suggestion["suggestion"].lower()
