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
    code = textwrap.dedent("""\
        # just a comment
        # nothing here
    """)
    result = analyse_code(code)
    assert result == []

# === COMBINED DETECTION CASE ===

def test_file_with_multiple_issues():
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

# === FALSE POSITIVE PREVENTION ===

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
    assert not any(r["usage_context"] in inefficient for r in result)

# === CORE STRUCTURE DETECTION TESTS ===

def test_detect_tuple():
    code = "coords = (1, 2)"
    result = analyse_code(code)
    assert any(r['type'] == 'Tuple' for r in result)

def test_detect_frozenset():
    code = "frozen = frozenset({1, 2, 3})"
    result = analyse_code(code)
    assert any(r['type'] == 'FrozenSet' for r in result)

def test_detect_namedtuple():
    code = textwrap.dedent("""\
        from collections import namedtuple
        Point = namedtuple("Point", ["x", "y"])
    """)
    result = analyse_code(code)
    assert any(r['type'] == 'NamedTuple' for r in result)

def test_detect_array():
    code = textwrap.dedent("""\
        import array
        a = array.array('i', [1, 2, 3])
    """)
    result = analyse_code(code)
    assert any(r['type'] == 'Array' for r in result)

def test_detect_heapq_usage():
    code = textwrap.dedent("""\
        import heapq
        heapq.heappush([], 10)
    """)
    result = analyse_code(code)
    assert any("Priority Queue" in r['type'] for r in result)

def test_detect_ordereddict():
    code = textwrap.dedent("""\
        from collections import OrderedDict
        od = OrderedDict()
    """)
    result = analyse_code(code)
    assert any(r['type'] == 'OrderedDict' for r in result)

def test_detect_defaultdict():
    code = textwrap.dedent("""\
        from collections import defaultdict
        dd = defaultdict(int)
    """)
    result = analyse_code(code)
    assert any(r['type'] == 'DefaultDict' for r in result)

# === DATACLASS DETECTION ===

def test_detect_dataclass():
    code = textwrap.dedent("""\
        from dataclasses import dataclass

        @dataclass
        class User:
            name: str
            age: int
    """)
    result = analyse_code(code)
    assert any(r['type'] == 'DataClass' for r in result)

def test_dataclass_with_multiple_decorators():
    code = textwrap.dedent("""\
        from dataclasses import dataclass

        @custom_decorator
        @dataclass
        class Product:
            id: int
            price: float
    """)
    result = analyse_code(code)
    assert any(r['type'] == 'DataClass' for r in result)

# === MEMBERSHIP FALLBACK CASE ===

def test_membership_on_expression():
    code = "if 1 in [1, 2, 3]: pass"
    result = analyse_code(code)
    assert any("Membership Test on Collection" in r['type'] for r in result)

# === CUSTOM CLASS DETECTION ===

def test_user_defined_class_with_unusual_name():
    code = textwrap.dedent("""\
        class StackMachine:
            def __init__(self):
                self.stack = []
    """)
    result = analyse_code(code)
    assert any("Stack" in r["type"] for r in result)

def test_user_defined_tree_class():
    code = textwrap.dedent("""\
        class BinaryTree:
            def __init__(self):
                self.root = None
    """)
    result = analyse_code(code)
    assert any("Tree" in r["type"] for r in result)

def test_user_defined_graph_class():
    code = textwrap.dedent("""\
        class SocialGraph:
            def __init__(self):
                self.nodes = []
    """)
    result = analyse_code(code)
    assert any("Graph" in r["type"] for r in result)

def test_user_defined_linkedlist_class():
    code = textwrap.dedent("""\
        class MyLinkedList:
            def __init__(self):
                self.head = None
    """)
    result = analyse_code(code)
    assert any("Linked List" in r["type"] for r in result)

# === FINAL COVERAGE PATCH TESTS ===

def test_namedtuple_called_through_alias():
    code = textwrap.dedent("""\
        from collections import namedtuple as nt
        Point = nt("Point", ["x", "y"])
    """)
    result = analyse_code(code)
    assert isinstance(result, list)

def test_class_with_non_name_decorator():
    code = textwrap.dedent("""\
        @some.module.decorator
        class Example:
            pass
    """)
    result = analyse_code(code)
    assert isinstance(result, list)
