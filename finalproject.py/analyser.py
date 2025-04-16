# analyser.py

import ast

class DataStructureAnalyzer(ast.NodeVisitor):
    """
    Walks an Abstract Syntax Tree (AST) and identifies data structure usage patterns,
    including both built-in and collections-based structures. Also flags inefficient
    usage patterns for later optimisation suggestions.
    """

    def __init__(self):
        # List of detected structure usages with metadata (line, type, notes)
        self.data_structures = []
        # Tracks variable names assigned to sets
        self.known_sets = set()
        # Tracks variable names assigned to deques
        self.known_deques = set()

    def record_structure(self, node, struct_type, details="", usage_context=None):
        """
        Adds a detected structure to the internal record list.

        Parameters:
        - node: The AST node where the structure was found
        - struct_type: The type of structure detected (e.g., List, Set, Deque)
        - details: Explanation or description of the structure usage
        - usage_context: Optional context tag (used for rule-based suggestions)
        """
        self.data_structures.append({
            "line": node.lineno,
            "type": struct_type,
            "details": details,
            "usage_context": usage_context
        })

    def is_known_set(self, node):
        """
        Determines if a given AST node is a variable name that refers to a known set.
        """
        return isinstance(node, ast.Name) and node.id in self.known_sets

    def is_known_deque(self, node):
        """
        Determines if a given AST node is a variable name that refers to a known deque.
        """
        return isinstance(node, ast.Name) and node.id in self.known_deques

    # === BASIC STRUCTURE DETECTION ===

    def visit_List(self, node):
        # Detect list literals: []
        self.record_structure(node, "List", "Ordered, mutable, allows duplicates.")
        self.generic_visit(node)

    def visit_Tuple(self, node):
        # Detect tuple literals: ()
        self.record_structure(node, "Tuple", "Ordered, immutable, allows duplicates.")
        self.generic_visit(node)

    def visit_Set(self, node):
        # Detect set literals: {1, 2, 3}
        self.record_structure(node, "Set", "Unordered, mutable, no duplicates.")
        self.generic_visit(node)

    def visit_Dict(self, node):
        # Detect dictionary literals: {"key": "value"}
        self.record_structure(node, "Dictionary", "Key-value pairs, mutable, ordered since Python 3.7+.")
        self.generic_visit(node)

    def visit_ListComp(self, node):
        # Detect list comprehensions: [x for x in iterable]
        self.record_structure(node, "List", "List comprehension (implicit list construction).")
        self.generic_visit(node)

    # === SPECIAL STRUCTURES & CALLS ===

    def visit_Call(self, node):
        """
        Detect structure calls such as deque(), Counter(), redundant patterns, etc.
        Uses delegated helper methods to handle complexity cleanly.
        """
        self.detect_structure_constructors(node)
        self.detect_redundant_conversions(node)
        self.detect_reversed_temp_list(node)
        self.generic_visit(node)

    def detect_structure_constructors(self, node):
        """
        Detect direct constructor calls for known data structures from collections and libraries.
        """
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            if func_name == "deque":
                self.record_structure(node, "Deque", "Fast queue operations (collections.deque).")

            elif func_name == "Counter":
                self.record_structure(node, "Counter", "Counts elements (collections.Counter).")

            elif func_name == "OrderedDict":
                self.record_structure(node, "OrderedDict", "Preserves insertion order (collections.OrderedDict).")

            elif func_name == "defaultdict":
                self.record_structure(node, "DefaultDict", "Auto-initialising dictionary (collections.defaultdict).")

            elif func_name == "frozenset":
                self.record_structure(node, "FrozenSet", "Immutable set, hashable.")

            elif func_name == "namedtuple":
                self.record_structure(node, "NamedTuple", "Lightweight immutable object with named fields.")

            elif func_name in {"heapq", "heappush", "heappop"}:
                self.record_structure(node, "Priority Queue", "Heap-based priority queue (heapq module).")

        elif isinstance(node.func, ast.Attribute):
            # Detect patterns like heapq.heappush(), array.array()
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "heapq" and node.func.attr in {"heappush", "heappop"}:
                    self.record_structure(node, "Priority Queue", "Heap-based priority queue (heapq).")

                if node.func.value.id == "array" and node.func.attr == "array":
                    self.record_structure(node, "Array", "Memory-efficient array (array.array).")

    def detect_redundant_conversions(self, node):
        """
        Detect patterns like list(set(...)) or set(list(...)) which are often unnecessary.
        """
        if isinstance(node.func, ast.Name) and node.func.id in {"list", "set"}:
            if len(node.args) == 1 and isinstance(node.args[0], ast.Call):
                inner = node.args[0]
                if isinstance(inner.func, ast.Name):
                    outer = node.func.id
                    inner_func = inner.func.id
                    if {outer, inner_func} == {"list", "set"}:
                        self.record_structure(
                            node,
                            "Redundant Conversion",
                            f"{outer}({inner_func}(...)) detected — may be redundant.",
                            usage_context="redundant_conversion"
                        )

    def detect_reversed_temp_list(self, node):
        """
        Detect inefficient reversed(list(...)) pattern, which creates an unnecessary copy.
        """
        if isinstance(node.func, ast.Name) and node.func.id == "reversed":
            if len(node.args) == 1 and isinstance(node.args[0], ast.Call):
                inner_call = node.args[0]
                if isinstance(inner_call.func, ast.Name) and inner_call.func.id == "list":
                    self.record_structure(
                        node,
                        "Reversed List",
                        "reversed(list(...)) detected — creates unnecessary temporary list.",
                        usage_context="reversed_temp_list"
                    )

    # === ASSIGNMENT-BASED DETECTION ===

    def visit_Assign(self, node):
        """
        Tracks assignments to mark variables as sets/deques and detect counter patterns.
        """
        if isinstance(node.value, ast.Set):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.known_sets.add(target.id)

        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == "deque":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.known_deques.add(target.id)

        if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
            left = node.value.left
            if isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute):
                if left.func.attr == "get":
                    self.record_structure(
                        node,
                        "Dictionary",
                        "Manual counter pattern (dict.get + 1).",
                        usage_context="manual_counter"
                    )

        self.generic_visit(node)

    # === CONTEXTUAL DETECTION ===

    def visit_If(self, node):
        """
        Detect inefficient membership checks: `if x in list`, suggest set usage instead.
        """
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            collection = node.test.comparators[0]
            collection_name = collection.id if isinstance(collection, ast.Name) else "Collection"

            is_efficient = isinstance(collection, ast.Set) or self.is_known_set(collection)

            note = (
                "Membership test detected (efficient — using set)." if is_efficient
                else "Membership test detected (consider using set)."
            )

            self.record_structure(
                node,
                f"Membership Test on {collection_name}",
                note,
                usage_context="membership_test"
            )

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """
        Detect use of .append(), .pop(), .popleft(), and assess efficiency depending on structure.
        """
        if node.attr in {"append", "pop", "popleft", "appendleft"}:
            var_name = node.value.id if isinstance(node.value, ast.Name) else None
            is_efficient = self.is_known_deque(node.value) if var_name else False

            note = (
                f"{node.attr} usage detected (efficient — using deque)." if is_efficient
                else f"{node.attr} usage detected (may indicate inefficient queue use)."
            )

            self.record_structure(
                node,
                "Deque" if is_efficient else "List",
                note,
                usage_context="append_or_pop"
            )

        self.generic_visit(node)

    # === FOR LOOP DETECTION ===

    def visit_For(self, node):
        """
        Detects inefficient loops over dict.keys()/values()/items()
        and manual dict construction in loop body.
        """
        # Rule 4: Detect inefficient .keys(), .values(), .items() iteration
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute):
            attr = node.iter.func.attr
            if attr in {"keys", "values", "items"} and isinstance(node.iter.func.value, ast.Name):
                self.record_structure(
                    node,
                    "Dictionary Iteration",
                    f"Iteration over dict.{attr}() detected.",
                    usage_context="dict_keys_loop"
                )

        # Rule 6: Detect manual dictionary building via loop
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                if (
                    isinstance(stmt.targets[0], ast.Subscript) and
                    isinstance(stmt.targets[0].value, ast.Name)
                ):
                    target_var = stmt.targets[0].value.id
                    self.record_structure(
                        stmt,
                        "Manual Dict Construction",
                        f"Manual dict built via loop to `{target_var}`.",
                        usage_context="manual_dict_loop"
                    )

        self.generic_visit(node)

    # === CLASS-BASED STRUCTURE DETECTION ===

    def visit_ClassDef(self, node):
        """
        Detects user-defined data structures based on class name patterns
        and dataclass decorators.
        """
        class_name = node.name.lower()

        if "stack" in class_name:
            self.record_structure(node, "User-Defined Stack", "LIFO structure.")
        elif "queue" in class_name:
            self.record_structure(node, "User-Defined Queue", "FIFO structure.")
        elif "linkedlist" in class_name:
            self.record_structure(node, "User-Defined Linked List", "Custom linked list.")
        elif "tree" in class_name:
            self.record_structure(node, "User-Defined Tree", "Custom tree structure.")
        elif "graph" in class_name:
            self.record_structure(node, "User-Defined Graph", "Custom graph structure.")

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                self.record_structure(node, "DataClass", "Structured data container (Python 3.7+).")

        self.generic_visit(node)

# === ENTRY POINT FUNCTION ===

def analyse_code(code_str):
    """
    Parses a string of Python code into an AST and analyses it for data structure patterns.
    Returns a list of detected structures with details and suggestions.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        raise ValueError(f"Syntax error while parsing code: {e}")

    analyser = DataStructureAnalyzer()
    analyser.visit(tree)
    return analyser.data_structures
