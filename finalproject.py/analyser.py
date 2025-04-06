import ast

class DataStructureAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python code to detect data structure usage and patterns.
    Records:
    - Structure type
    - Line number
    - Usage context (e.g., membership tests, manual counters)
    """

    def __init__(self):
        self.data_structures = []

        # Track variable names assigned to set literals (for smarter membership detection)
        self.known_sets = set()
        
        self.known_deques = set()

    def record_structure(self, node, struct_type, details="", usage_context=None):
        """
        Stores details about each detected data structure or usage pattern.
        """
        self.data_structures.append({
            "line": node.lineno,
            "type": struct_type,
            "details": details,
            "usage_context": usage_context
        })

    # === BASIC STRUCTURE DETECTION ===

    def visit_List(self, node):
        self.record_structure(node, "List", "Ordered, mutable, allows duplicates.")
        self.generic_visit(node)

    def visit_Tuple(self, node):
        self.record_structure(node, "Tuple", "Ordered, immutable, allows duplicates.")
        self.generic_visit(node)

    def visit_Set(self, node):
        self.record_structure(node, "Set", "Unordered, mutable, no duplicates.")
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.record_structure(node, "Dictionary", "Key-value pairs, mutable, ordered since Python 3.7+.")
        self.generic_visit(node)
        
    def visit_ListComp(self, node):
        self.record_structure(
            node,
            "List",
            "List comprehension (implicit list construction)."
        )
        self.generic_visit(node)


    # === SPECIAL STRUCTURES & MODULES ===

    def visit_Call(self, node):
        """
        Detects special data structures like:
        - collections (deque, Counter, defaultdict, OrderedDict)
        - array.array
        - heapq functions
        - namedtuple
        - frozenset
        """
        # Handle direct function calls like deque(), Counter(), etc.
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
            # Detect heapq.heappush / heapq.heappop
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "heapq" and node.func.attr in {"heappush", "heappop"}:
                    self.record_structure(node, "Priority Queue", "Heap-based priority queue (heapq).")

            # Detect array.array
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "array":
                if node.func.attr == "array":
                    self.record_structure(node, "Array", "Memory-efficient array (array.array).")


        self.generic_visit(node)

    # === ASSIGNMENT-BASED DETECTION ===

    def visit_Assign(self, node):
        """
        Tracks:
        - set assignments for efficient membership tests
        - deque assignments to avoid false suggestions
        - manual counter patterns using dict.get(...)
        """

        # Track set assignments
        if isinstance(node.value, ast.Set):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.known_sets.add(target.id)

        # Track deque assignments
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == "deque":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.known_deques.add(target.id)


        # Detect manual counter pattern
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



    # === CONTEXT-BASED DETECTION ===

    def visit_If(self, node):
        """
        Detects all membership tests: `if x in y`
        Records whether the test is efficient or inefficient.
        """
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            collection = node.test.comparators[0]
            collection_name = collection.id if isinstance(collection, ast.Name) else "Collection"

            # Determine if this is efficient usage (set literal or known set variable)
            is_efficient = (
                isinstance(collection, ast.Set) or
                (isinstance(collection, ast.Name) and collection.id in self.known_sets)
            )

            # Generate description string with keyword 'efficient' if applicable
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
        Detects all queue-related usage patterns:
        - .append(), .pop(), .popleft(), .appendleft()
        Records them all, but only marks them efficient if using deque().
        """

        if node.attr in {"append", "pop", "popleft", "appendleft"}:
            var_name = None
            if isinstance(node.value, ast.Name):
                var_name = node.value.id

            # ✅ Debug this:
            is_efficient = var_name in self.known_deques if var_name else False
            print(f"[DEBUG is_efficient?] var: {var_name}, known_deques: {self.known_deques}, result: {is_efficient}")

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







    # === CLASS-BASED STRUCTURE DETECTION ===

    def visit_ClassDef(self, node):
        """
        Detects user-defined structures:
        - Stack, Queue, LinkedList, Tree, Graph
        Also detects @dataclass usage.
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

        # Detect @dataclass decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                self.record_structure(node, "DataClass", "Structured data container (Python 3.7+).")

        self.generic_visit(node)

# === ENTRY POINT ===

def analyse_code(code_str):
    """
    Main interface for analysing a block of Python code.
    Returns a list of detected data structures and usage patterns.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        raise ValueError(f"Syntax error while parsing code: {e}")

    analyser = DataStructureAnalyzer()
    analyser.visit(tree)
    return analyser.data_structures
