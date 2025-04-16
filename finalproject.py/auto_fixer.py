import ast
import astor

class FixPlan:
    """
    Represents a fix to be injected into the AST after a given variable assignment.
    Used to support fixes like replacing list-based membership checks with set-based ones,
    by injecting a line like `_x_set = set(x)` right after `x = [...]`.
    """
    def __init__(self, target_var, injected_code, replace_node=None):
        self.target_var = target_var
        self.injected_code = injected_code
        self.replace_node = replace_node

class AutoFixer(ast.NodeTransformer):
    """
    Traverses and transforms a Python AST to apply optimisations for data structure usage.
    Implements multiple transformation rules targeting inefficient Python patterns.
    """

    def __init__(self):
        # Maps variable names to set(...) injection fix plans (Rule 1)
        self.inject_after_var = {}

        # Tracks any required import statements like 'from collections import deque'
        self.imports_needed = set()

        # Tracks variable names that should be rewritten as deque instead of list
        self.deque_vars = set()

        # Tracks variable assignments to lists and sets
        self.assignment_map = {}

        # Stores (original for-loop node, replacement dict comprehension node)
        self.manual_dict_loop_fixes = []

        # Indicates whether any changes were made
        self.changed = False

    def visit_If(self, node):
        # Rule 1: Replace 'if x in list' → 'if x in set(...)'
        self.replace_list_membership_with_set(node)
        return self.generic_visit(node)

    def replace_list_membership_with_set(self, node):
        """
        Finds membership tests (e.g. `if item in list`) and injects a set conversion
        if the target variable is not already a set.
        """
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            collection = node.test.comparators[0]
            if isinstance(collection, ast.Name):
                list_var = collection.id

                # Skip fix if the variable is already assigned as a set
                if list_var in self.assignment_map:
                    assigned_node = self.assignment_map[list_var]
                    if isinstance(assigned_node.value, ast.Set):
                        return

                # Replace the membership test with one that checks a set copy
                set_var = f"_{list_var}_set"
                node.test.comparators[0] = ast.Name(id=set_var, ctx=ast.Load())

                # Inject the line: _list_var_set = set(list_var)
                assign = ast.Assign(
                    targets=[ast.Name(id=set_var, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="set", ctx=ast.Load()),
                        args=[ast.Name(id=list_var, ctx=ast.Load())],
                        keywords=[]
                    )
                )
                self.inject_after_var[list_var] = FixPlan(list_var, assign)
                self.changed = True

    def visit_Expr(self, node):
        # Rule 3: Replace q.pop(0) → q.popleft() and track variable for deque conversion
        self.replace_pop_zero_with_popleft(node)
        return self.generic_visit(node)

    def replace_pop_zero_with_popleft(self, node):
        """
        Replaces inefficient list-based queue operations like pop(0)
        with deque.popleft() and records that the variable must be converted to deque.
        """
        if isinstance(node.value, ast.Call):
            call = node.value
            if (
                isinstance(call.func, ast.Attribute)
                and call.func.attr == "pop"
                and len(call.args) == 1
                and isinstance(call.args[0], ast.Constant)
                and call.args[0].value == 0
            ):
                call.func.attr = "popleft"
                call.args = []
                if isinstance(call.func.value, ast.Name):
                    var_name = call.func.value.id
                    self.deque_vars.add(var_name)
                    self.imports_needed.add("from collections import deque")
                    self.changed = True

    def visit_For(self, node):
        # Rule 4: Replace 'for k in d.keys()' → 'for k in d'
        # Rule 6: Convert manual dict building to a dict comprehension
        self.replace_dict_keys_loop(node)
        self.replace_manual_dict_building(node)
        return self.generic_visit(node)

    def replace_dict_keys_loop(self, node):
        """
        Rewrites loops using dict.keys() to direct iteration over the dictionary.
        """
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute):
            if node.iter.func.attr == "keys" and isinstance(node.iter.func.value, ast.Name):
                node.iter = ast.Name(id=node.iter.func.value.id, ctx=ast.Load())
                self.changed = True

    def replace_manual_dict_building(self, node):
        """
        Detects loops manually building a dictionary like:
            for k, v in pairs:
                d[k] = v
        and rewrites them as a dictionary comprehension.
        """
        if len(node.body) != 1:
            return

        stmt = node.body[0]
        if not isinstance(stmt, ast.Assign):
            return

        # Check that the assignment is in the form: d[k] = v
        if (
            isinstance(stmt.targets[0], ast.Subscript)
            and isinstance(stmt.targets[0].value, ast.Name)
            and isinstance(stmt.targets[0].slice, ast.Name)
        ):
            dict_var = stmt.targets[0].value.id
            key_var = stmt.targets[0].slice.id

            if isinstance(stmt.value, ast.Name):
                value_var = stmt.value.id

                # Check for loop target: for k, v in ...
                if (
                    isinstance(node.target, ast.Tuple)
                    and len(node.target.elts) == 2
                    and isinstance(node.target.elts[0], ast.Name)
                    and isinstance(node.target.elts[1], ast.Name)
                ):
                    tk = node.target.elts[0].id
                    tv = node.target.elts[1].id

                    if key_var == tk and value_var == tv:
                        # Construct the dict comprehension replacement
                        new_node = ast.Assign(
                            targets=[ast.Name(id=dict_var, ctx=ast.Store())],
                            value=ast.DictComp(
                                key=ast.Name(id=key_var, ctx=ast.Load()),
                                value=ast.Name(id=value_var, ctx=ast.Load()),
                                generators=[ast.comprehension(
                                    target=node.target,
                                    iter=node.iter,
                                    ifs=[],
                                    is_async=0
                                )]
                            )
                        )
                        self.manual_dict_loop_fixes.append((node, new_node))
                        self.changed = True

    def visit_Call(self, node):
        # Rule 5 and 7: inline call transformations
        node = self.replace_redundant_conversion(node)
        node = self.replace_reversed_temp_list(node)
        return self.generic_visit(node)

    def replace_redundant_conversion(self, node):
        """
        Replaces nested list/set calls like list(set(...)) with just set(...)
        """
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in {"list", "set"}
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Name)
            and node.args[0].func.id in {"list", "set"}
        ):
            inner_arg = node.args[0].args[0] if node.args[0].args else None
            if "set" in {node.func.id, node.args[0].func.id} and inner_arg:
                self.changed = True
                return ast.Call(
                    func=ast.Name(id="set", ctx=ast.Load()),
                    args=[self.visit(inner_arg)],
                    keywords=[]
                )
        return node

    def replace_reversed_temp_list(self, node):
        """
        Replaces reversed(list(...)) with reversed(...) directly.
        """
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "reversed"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Name)
            and node.args[0].func.id == "list"
        ):
            inner_arg = node.args[0].args[0] if node.args[0].args else None
            if inner_arg:
                self.changed = True
                return ast.Call(
                    func=ast.Name(id="reversed", ctx=ast.Load()),
                    args=[self.visit(inner_arg)],
                    keywords=[]
                )
        return node

    def visit_Assign(self, node):
        # Handles OrderedDict replacement and variable tracking
        self.track_list_assignment_for_deque(node)
        self.replace_ordereddict_with_dict(node)
        return self.generic_visit(node)

    def track_list_assignment_for_deque(self, node):
        # Track any list/set assignment to help context-aware fixes later
        if isinstance(node.value, (ast.List, ast.Set)):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.assignment_map[target.id] = node

    def replace_ordereddict_with_dict(self, node):
        # Matches OrderedDict() usage and replaces it with {}
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "OrderedDict"
        ):
            node.value = ast.Dict(keys=[], values=[])
            self.changed = True

    def apply_fixes(self, tree):
        """
        Finalises all rewrites by injecting transformations into the AST body.
        This includes replacing assignments, adding new lines, and rewiring loops.
        """
        new_body = []

        for stmt in tree.body:
            # Convert flagged list assignment to deque
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id in self.deque_vars
                        and isinstance(stmt.value, ast.List)
                    ):
                        stmt.value = ast.Call(
                            func=ast.Name(id="deque", ctx=ast.Load()),
                            args=[stmt.value],
                            keywords=[]
                        )
                        self.changed = True

            new_body.append(stmt)

            # Inject any set(...) assignments after their original variables
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if var_name in self.inject_after_var:
                            new_body.append(self.inject_after_var[var_name].injected_code)

        # Apply loop-to-dict-comprehension rewrites
        for old_node, new_node in self.manual_dict_loop_fixes:
            new_body = [new_node if stmt == old_node else stmt for stmt in new_body]

        tree.body = new_body
        return tree

def apply_auto_fixes(code):
    """
    Main entry point: Parses code into AST, applies all rewrites,
    and returns the updated source code string along with a change flag.
    """
    tree = ast.parse(code)
    fixer = AutoFixer()
    tree = fixer.visit(tree)
    tree = fixer.apply_fixes(tree)

    fixed_code = astor.to_source(tree)
    import_lines = "\n".join(sorted(fixer.imports_needed)) + "\n" if fixer.imports_needed else ""
    return import_lines + fixed_code, fixer.changed
