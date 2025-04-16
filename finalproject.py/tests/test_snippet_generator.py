# test_snippet_generator.py

from snippet_generator import get_fix_snippet

# Test fix snippet for manual counter pattern using collections.Counter
def test_counter_snippet():
    suggestion = {
        "suggestion": "Use collections.Counter instead of manual dictionary counting.",
        "usage_context": "manual_counter",
        "current_type": "Dictionary"
    }
    snippet = get_fix_snippet(suggestion)
    assert "Counter" in snippet
    assert "update" in snippet

# Test fix snippet for membership test using a set instead of list
def test_membership_test_snippet():
    suggestion = {
        "suggestion": "Use a set for membership testing.",
        "usage_context": "membership_test",
        "current_type": "Membership Test on list"
    }
    snippet = get_fix_snippet(suggestion)
    assert "set" in snippet
    assert "if item in data" in snippet

# Test fix snippet for queue pattern using deque
def test_deque_snippet():
    suggestion = {
        "suggestion": "Consider using collections.deque for queue operations.",
        "usage_context": "append_or_pop",
        "current_type": "List"
    }
    snippet = get_fix_snippet(suggestion)
    assert "deque" in snippet
    assert "popleft" in snippet

# Test fix snippet for dict.keys() loop suggesting direct dictionary iteration
def test_dict_keys_loop_snippet():
    suggestion = {
        "suggestion": "Iterate directly over the dictionary instead of using .keys().",
        "usage_context": "dict_keys_loop",
        "current_type": "Dictionary Iteration"
    }
    snippet = get_fix_snippet(suggestion)
    assert "for key in my_dict" in snippet

# Test fix snippet for redundant list(set(...)) or set(list(...)) conversion
def test_redundant_conversion_snippet():
    suggestion = {
        "suggestion": "Avoid redundant wrapping like list(set(...)) or set(list(...)).",
        "usage_context": "redundant_conversion",
        "current_type": "Redundant Conversion"
    }
    snippet = get_fix_snippet(suggestion)
    assert "Remove unnecessary wrapping" in snippet
    assert "set(data)" in snippet or "list(data)" in snippet

# Test fix snippet for manual dictionary construction using dict comprehension
def test_dict_comprehension_snippet():
    suggestion = {
        "suggestion": "Use dict comprehension.",
        "usage_context": "manual_dict_loop",
        "current_type": "Dictionary"
    }
    snippet = get_fix_snippet(suggestion)
    assert "for k, v in pairs" in snippet

# Test fix snippet for reversed(list(...)) pattern using reversed() directly
def test_reversed_temp_list_snippet():
    suggestion = {
        "suggestion": "Avoid reversing a temporary list. Use reversed() on existing sequences.",
        "usage_context": "reversed_temp_list",
        "current_type": "Reversed List"
    }
    snippet = get_fix_snippet(suggestion)
    assert "reversed" in snippet
    assert "for item in reversed(data)" in snippet

# Test fix snippet for using OrderedDict
def test_ordereddict_snippet():
    suggestion = {
        "suggestion": "Use a plain dict instead of OrderedDict if order isn’t needed.",
        "usage_context": "",
        "current_type": "OrderedDict"
    }
    snippet = get_fix_snippet(suggestion)
    assert "OrderedDict" in snippet
    assert "[\"key\"]" in snippet

# Test fix snippet for using defaultdict for auto-initialising dictionaries
def test_defaultdict_snippet():
    suggestion = {
        "suggestion": "Use collections.defaultdict for auto-initialising dictionaries.",
        "usage_context": "manual_counter",
        "current_type": "Dictionary"
    }
    snippet = get_fix_snippet(suggestion)
    assert "defaultdict" in snippet
    assert "d[key] += 1" in snippet

# Test fallback snippet for unmatched suggestion patterns
def test_fallback_snippet():
    suggestion = {
        "suggestion": "Some generic suggestion not tied to a specific pattern.",
        "usage_context": "unknown_context",
        "current_type": "Tuple"
    }
    snippet = get_fix_snippet(suggestion)
    assert "No fix snippet available" in snippet
