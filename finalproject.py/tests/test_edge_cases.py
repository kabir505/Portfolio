import pytest
import textwrap
from analyser import analyse_code

# === BASIC EDGE CASES ===

def test_empty_file():
    code = ""
    result = analyse_code(code)
    assert result == []

def test_file_with_syntax_error():
    code = "def broken_func(:"
    with pytest.raises(ValueError) as e:
        analyse_code(code)
    assert "Syntax error" in str(e.value)

def test_file_with_no_structures():
    code = "print('Hello, world!')"
    result = analyse_code(code)
    assert result == []

def test_file_with_only_comments():
    code = "# just a comment\n# nothing here"
    result = analyse_code(code)
    assert result == []

# === COMBINED PATTERN CASE ===

def test_file_with_multiple_patterns():
    code = textwrap.dedent("""\
        numbers = [1, 2, 3]
        if 2 in numbers:
            print("Found")

        count_dict = {}
        count_dict['x'] = count_dict.get('x', 0) + 1

        mylist = []
        mylist.append(5)
        mylist.pop(0)
    """)
    result = analyse_code(code)
    contexts = [r.get("usage_context") for r in result]
    assert "membership_test" in contexts
    assert "manual_counter" in contexts
    assert "append_or_pop" in contexts

# === FALSE POSITIVE TEST ===

def test_file_with_no_suggestions_needed():
    code = textwrap.dedent("""\
        from collections import Counter, deque

        numbers = {1, 2, 3}
        if 3 in numbers:
            print("Found")

        counter = Counter()
        counter.update("hello")

        q = deque()
        q.append(1)
        x = q.popleft()
    """)
    result = analyse_code(code)
    inefficient = {"membership_test", "manual_counter", "append_or_pop"}
    has_false_positive = any(
        r["usage_context"] in inefficient and "efficient" not in r["details"].lower()
        for r in result
    )
    assert not has_false_positive

# === ADVANCED STRUCTURE DETECTION ===

def test_detect_tuple():
    assert any(r['type'] == 'Tuple' for r in analyse_code("x = (1, 2)"))

def test_detect_frozenset():
    assert any(r['type'] == 'FrozenSet' for r in analyse_code("x = frozenset([1, 2])"))

def test_detect_namedtuple():
    code = textwrap.dedent("""\
        from collections import namedtuple
        Point = namedtuple("Point", ["x", "y"])
    """)
    assert any(r['type'] == 'NamedTuple' for r in analyse_code(code))

def test_detect_array():
    code = textwrap.dedent("""\
        import array
        a = array.array('i', [1, 2, 3])
    """)
    assert any(r['type'] == 'Array' for r in analyse_code(code))

def test_detect_heapq():
    code = "import heapq\nheapq.heappush([], 1)"
    assert any("Priority Queue" in r['type'] for r in analyse_code(code))

def test_detect_ordereddict():
    code = "from collections import OrderedDict\nx = OrderedDict()"
    assert any(r['type'] == 'OrderedDict' for r in analyse_code(code))

def test_detect_defaultdict():
    code = "from collections import defaultdict\nd = defaultdict(int)"
    assert any(r['type'] == 'DefaultDict' for r in analyse_code(code))

# === DATACLASS DETECTION ===

def test_detect_dataclass():
    code = textwrap.dedent("""\
        from dataclasses import dataclass
        @dataclass
        class User:
            name: str
            age: int
    """)
    assert any(r['type'] == 'DataClass' for r in analyse_code(code))

def test_dataclass_with_multiple_decorators():
    code = textwrap.dedent("""\
        from dataclasses import dataclass
        @some.decorator
        @dataclass
        class Product:
            id: int
            price: float
    """)
    assert any(r['type'] == 'DataClass' for r in analyse_code(code))

# === CUSTOM CLASS DETECTION ===

def test_user_defined_stack():
    code = "class StackMachine:\n    def __init__(self): self.stack = []"
    assert any("Stack" in r["type"] for r in analyse_code(code))

def test_user_defined_tree():
    code = "class BinaryTree:\n    def __init__(self): self.root = None"
    assert any("Tree" in r["type"] for r in analyse_code(code))

def test_user_defined_graph():
    code = "class SocialGraph:\n    def __init__(self): self.nodes = []"
    assert any("Graph" in r["type"] for r in analyse_code(code))

def test_user_defined_linkedlist():
    code = "class MyLinkedList:\n    def __init__(self): self.head = None"
    assert any("Linked List" in r["type"] for r in analyse_code(code))

# === EDGE CASES FOR RULES 4–8 ===

def test_keys_loop_with_whitespace():
    code = "d = {'a': 1}\nfor k in d.keys( ): print(k)"
    assert any(r["usage_context"] == "dict_keys_loop" for r in analyse_code(code))

def test_redundant_conversion_nested():
    code = "x = list(set((1, 2, 3)))"
    assert any(r["usage_context"] == "redundant_conversion" for r in analyse_code(code))

def test_non_redundant_conversion():
    code = "x = set((1, 2, 3))"
    result = analyse_code(code)
    assert all(r["usage_context"] != "redundant_conversion" for r in result)

def test_manual_dict_loop_with_calc():
    code = "d = {}\nfor k, v in [('a', 1)]: d[k] = v + 1"
    assert any(r["usage_context"] == "manual_dict_loop" for r in analyse_code(code))

def test_reversed_on_existing_list_skips():
    code = "data = [1, 2, 3]\nfor x in reversed(data): pass"
    assert all(r["usage_context"] != "reversed_temp_list" for r in analyse_code(code))

def test_ordereddict_with_special_usage_skips():
    code = textwrap.dedent("""\
        from collections import OrderedDict
        d = OrderedDict()
        d['a'] = 1
        d.move_to_end('a')
    """)
    assert not any(r["usage_context"] == "ordered_dict_basic_usage" for r in analyse_code(code))
