# test_auto_fixer.py

from auto_fixer import apply_auto_fixes

# Test that inefficient membership with list is rewritten using set()
def test_membership_test_is_fixed():
    code = "numbers = [1, 2, 3]\nif 2 in numbers:\n    print('Found')"
    fixed_code, changed = apply_auto_fixes(code)
    assert "set(numbers)" in fixed_code
    assert "2 in _numbers_set" in fixed_code
    assert changed is True

# Test that list.pop(0) is replaced with deque().popleft()
def test_queue_like_list_pop_is_fixed():
    code = "q = [1, 2, 3]\nq.pop(0)"
    fixed_code, changed = apply_auto_fixes(code)
    assert "from collections import deque" in fixed_code
    assert "q = deque([1, 2, 3])" in fixed_code
    assert "q.popleft()" in fixed_code
    assert changed is True

# Test that dict.keys() is removed from for-loop
def test_dict_keys_loop_is_fixed():
    code = "d = {'a': 1}\nfor k in d.keys():\n    print(k)"
    fixed_code, changed = apply_auto_fixes(code)
    assert "for k in d:" in fixed_code
    assert ".keys()" not in fixed_code
    assert changed is True

# Test that manual dictionary building is converted to dict comprehension
def test_manual_dict_loop_is_fixed():
    code = "d = {}\nfor k, v in [('a', 1)]:\n    d[k] = v"
    fixed_code, changed = apply_auto_fixes(code)
    assert "d = {k: v for k, v in [('a', 1)]}" in fixed_code
    assert changed is True

# Test that list(set(...)) is simplified to set(...)
def test_redundant_conversion_is_fixed():
    code = "unique = list(set(['a', 'b', 'a']))"
    fixed_code, changed = apply_auto_fixes(code)
    assert "unique = set(['a', 'b', 'a'])" in fixed_code
    assert changed is True

# Test that reversed(list(...)) is simplified to reversed(...)
def test_reversed_list_is_fixed():
    code = "for item in reversed(list(data)):\n    print(item)"
    fixed_code, changed = apply_auto_fixes(code)
    assert "reversed(data)" in fixed_code
    assert "list(" not in fixed_code
    assert changed is True

# Test that OrderedDict usage is replaced with an empty dictionary
def test_ordereddict_is_fixed():
    code = "from collections import OrderedDict\nd = OrderedDict()"
    fixed_code, changed = apply_auto_fixes(code)
    assert "d = {}" in fixed_code
    assert changed is True
    # Note: We do not currently remove the import statement

# Test that no changes are made if the input is already optimal
def test_no_changes_for_optimal_code():
    code = "numbers = {1, 2, 3}\nif 2 in numbers:\n    print('Found')"
    fixed_code, changed = apply_auto_fixes(code)
    assert changed is False
    assert fixed_code.strip() == code.strip()
