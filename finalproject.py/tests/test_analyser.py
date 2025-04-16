# test_analyser.py

import pytest
from analyser import analyse_code

# BASIC DATA STRUCTURE DETECTION

# Test that a list literal is detected correctly
def test_detects_list():
    code = "x = [1, 2, 3]"
    result = analyse_code(code)
    assert any(s["type"] == "List" for s in result)

# Test that a tuple literal is detected correctly
def test_detects_tuple():
    code = "x = (1, 2, 3)"
    result = analyse_code(code)
    assert any(s["type"] == "Tuple" for s in result)

# Test that a set literal is detected correctly
def test_detects_set():
    code = "x = {1, 2, 3}"
    result = analyse_code(code)
    assert any(s["type"] == "Set" for s in result)

# Test that a dictionary literal is detected correctly
def test_detects_dict():
    code = "x = {'a': 1, 'b': 2}"
    result = analyse_code(code)
    assert any(s["type"] == "Dictionary" for s in result)

# Test that list comprehension is detected
def test_detects_list_comprehension():
    code = "[x for x in range(5)]"
    result = analyse_code(code)
    assert any(s["type"] == "List" and "comprehension" in s["details"].lower() for s in result)

# Test that Counter() usage is detected
def test_detects_counter():
    code = "from collections import Counter\nx = Counter()"
    result = analyse_code(code)
    assert any(s["type"] == "Counter" for s in result)

# Test that deque() usage is detected
def test_detects_deque():
    code = "from collections import deque\nx = deque()"
    result = analyse_code(code)
    assert any(s["type"] == "Deque" for s in result)

# Test that OrderedDict() usage is detected
def test_detects_ordereddict():
    code = "from collections import OrderedDict\nx = OrderedDict()"
    result = analyse_code(code)
    assert any(s["type"] == "OrderedDict" for s in result)

# Test that defaultdict() usage is detected
def test_detects_defaultdict():
    code = "from collections import defaultdict\nx = defaultdict(int)"
    result = analyse_code(code)
    assert any(s["type"] == "DefaultDict" for s in result)

# Test that frozenset() usage is detected
def test_detects_frozenset():
    code = "x = frozenset([1, 2, 3])"
    result = analyse_code(code)
    assert any(s["type"] == "FrozenSet" for s in result)

# Test that namedtuple() usage is detected
def test_detects_namedtuple():
    code = "from collections import namedtuple\nPoint = namedtuple('Point', 'x y')"
    result = analyse_code(code)
    assert any(s["type"] == "NamedTuple" for s in result)

# Test that heapq priority queue usage is detected
def test_detects_priority_queue():
    code = "import heapq\nheapq.heappush([], 3)"
    result = analyse_code(code)
    assert any(s["type"] == "Priority Queue" for s in result)

# Test that array.array() usage is detected
def test_detects_array():
    code = "import array\nx = array.array('i', [1, 2, 3])"
    result = analyse_code(code)
    assert any(s["type"] == "Array" for s in result)

# === USAGE CONTEXT / RULE-BASED DETECTION ===

# Test that a membership test using a list is tagged with usage_context
def test_usage_membership_test():
    code = "x = [1, 2, 3]\nif 2 in x:\n    pass"
    result = analyse_code(code)
    assert any(s["usage_context"] == "membership_test" for s in result)

# Test that manual counter pattern (dict.get + 1) is detected
def test_usage_manual_counter():
    code = "d = {}\nd['a'] = d.get('a', 0) + 1"
    result = analyse_code(code)
    assert any(s["usage_context"] == "manual_counter" for s in result)

# Test that append/pop usage resembling queue is detected
def test_usage_append_or_pop():
    code = "queue = []\nqueue.pop(0)"
    result = analyse_code(code)
    assert any(s["usage_context"] == "append_or_pop" for s in result)

# Test that dict.keys() iteration is detected
def test_usage_dict_keys_loop():
    code = "d = {'a': 1}\nfor k in d.keys():\n    print(k)"
    result = analyse_code(code)
    assert any(s["usage_context"] == "dict_keys_loop" for s in result)

# Test that list(set(...)) pattern is detected as redundant conversion
def test_usage_redundant_conversion():
    code = "x = list(set([1, 2, 3]))"
    result = analyse_code(code)
    assert any(s["usage_context"] == "redundant_conversion" for s in result)

# Test that manually building a dictionary inside a loop is detected
def test_usage_manual_dict_loop():
    code = "d = {}\nkeys = ['a']\nvals = [1]\nfor k, v in zip(keys, vals):\n    d[k] = v"
    result = analyse_code(code)
    assert any(s["usage_context"] == "manual_dict_loop" for s in result)

# Test that reversed(list(...)) usage is detected as inefficient
def test_usage_reversed_temp_list():
    code = "data = [1, 2, 3]\nfor x in reversed(list(data)):\n    pass"
    result = analyse_code(code)
    assert any(s["usage_context"] == "reversed_temp_list" for s in result)

# Sanity test that OrderedDict detection still works for structure type
def test_detects_ordereddict_structure():
    code = "from collections import OrderedDict\nx = OrderedDict()"
    result = analyse_code(code)
    assert any(s["type"] == "OrderedDict" for s in result)
