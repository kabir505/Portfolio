# import ast
# import astor

# class FixPlan:
#     def __init__(self, node, replacement_nodes, import_line=None):
#         self.node = node  # the node to replace
#         self.replacement_nodes = replacement_nodes  # list of AST nodes to inject
#         self.import_line = import_line

# class AutoFixer(ast.NodeTransformer):
#     def __init__(self):
#         self.fixes = []
#         self.imports_needed = set()

#     def visit_Assign(self, node):
#         # Match pattern: d[key] = d.get(key, 0) + 1 → Counter
#         if (
#             isinstance(node.value, ast.BinOp)
#             and isinstance(node.value.op, ast.Add)
#             and isinstance(node.value.left, ast.Call)
#             and isinstance(node.value.left.func, ast.Attribute)
#             and node.value.left.func.attr == "get"
#         ):
#             target = node.targets[0]
#             if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
#                 var_name = target.value.id

#                 original_line = astor.to_source(node).strip()
#                 comment_node = ast.Expr(value=ast.Constant(value=f"# {original_line}  # replaced by auto-fix"))

#                 fix_code = f"{var_name} = Counter()\n{var_name}.update(your_data_here)"
#                 fix_nodes = [comment_node] + ast.parse(fix_code).body

#                 self.fixes.append(FixPlan(node=node, replacement_nodes=fix_nodes, import_line="from collections import Counter"))
#                 return None

#         return self.generic_visit(node)

#     def visit_Expr(self, node):
#         # Match pattern: queue.pop(0) → queue.popleft()
#         if isinstance(node.value, ast.Call):
#             call = node.value
#             if (
#                 isinstance(call.func, ast.Attribute)
#                 and call.func.attr == "pop"
#                 and len(call.args) == 1
#                 and isinstance(call.args[0], ast.Constant)
#                 and call.args[0].value == 0
#             ):
#                 original_line = astor.to_source(node).strip()
#                 comment_node = ast.Expr(value=ast.Constant(value=f"# {original_line}  # replaced by auto-fix"))

#                 call.func.attr = "popleft"
#                 call.args = []
#                 fixed_node = ast.copy_location(node, node)

#                 self.fixes.append(FixPlan(node=node, replacement_nodes=[comment_node, fixed_node], import_line="from collections import deque"))
#                 return None

#         return self.generic_visit(node)

#     def visit_If(self, node):
#         # Match inefficient membership: if x in list → set(list)
#         if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
#             collection = node.test.comparators[0]
#             if isinstance(collection, ast.Name):
#                 list_var = collection.id
#                 temp_var = f"_{list_var}_set"

#                 original_line = astor.to_source(node).strip()
#                 comment_node = ast.Expr(value=ast.Constant(value=f"# {original_line}  # replaced by auto-fix"))

#                 # Create: _names_set = set(names)
#                 set_assign = ast.parse(f"{temp_var} = set({list_var})").body[0]

#                 # Rewrite the condition
#                 node.test.comparators[0] = ast.Name(id=temp_var, ctx=ast.Load())
#                 fixed_node = ast.copy_location(node, node)

#                 self.fixes.append(FixPlan(node=node, replacement_nodes=[set_assign, comment_node, fixed_node]))

#                 return None

#         return self.generic_visit(node)

#     def apply_fixes(self, tree):
#         new_body = []
#         replaced_nodes = {fix.node for fix in self.fixes if fix.node}

#         for stmt in tree.body:
#             if stmt in replaced_nodes:
#                 fix = next(f for f in self.fixes if f.node == stmt)
#                 new_body.extend(fix.replacement_nodes)
#             else:
#                 new_body.append(stmt)

#         # Add top-level insertions (e.g. for standalone fixes)
#         for plan in self.fixes:
#             if plan.node is None:
#                 new_body = plan.replacement_nodes + new_body

#         tree.body = new_body
#         return tree


#     def replace_node(self, tree, old_node, new_nodes):
#         class NodeReplacer(ast.NodeTransformer):
#             def __init__(self, old_node, new_nodes):
#                 self.old_node = old_node
#                 self.new_nodes = new_nodes

#             def visit_Module(self, node):
#                 new_body = []
#                 for stmt in node.body:
#                     if stmt == self.old_node:
#                         new_body.extend(self.new_nodes)
#                     else:
#                         new_body.append(stmt)
#                 node.body = new_body
#                 return node

#         replacer = NodeReplacer(old_node, new_nodes)
#         return replacer.visit(tree)

# def apply_auto_fixes(code):
#     tree = ast.parse(code)
#     fixer = AutoFixer()
#     tree = fixer.visit(tree)
#     tree = fixer.apply_fixes(tree)

#     fixed_code = astor.to_source(tree)

#     imports = {fix.import_line for fix in fixer.fixes if fix.import_line}
#     imports.update(fixer.imports_needed)
#     import_lines = "\n".join(sorted(filter(None, imports))) + "\n" if imports else ""

#     return import_lines + fixed_code, bool(fixer.fixes or fixer.imports_needed)



import ast
import astor

class FixPlan:
    def __init__(self, node, replacement_code, import_line=None):
        self.node = node
        self.replacement_code = replacement_code
        self.import_line = import_line

class AutoFixer(ast.NodeTransformer):
    def __init__(self):
        self.fixes = []
        self.imports_needed = set()
        self.vars_to_remove = set()

    def visit_Assign(self, node):
        # Match: d[key] = d.get(key, 0) + 1
        if (
            isinstance(node.value, ast.BinOp)
            and isinstance(node.value.op, ast.Add)
            and isinstance(node.value.left, ast.Call)
            and isinstance(node.value.left.func, ast.Attribute)
            and node.value.left.func.attr == "get"
        ):
            target = node.targets[0]
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                var_name = target.value.id
                print(f"[AUTO-FIX] Detected manual counter pattern in variable: {var_name}")
                fix_code = f"{var_name} = Counter()\n{var_name}.update(your_data_here)"
                self.fixes.append(FixPlan(node=None, replacement_code=fix_code, import_line="from collections import Counter"))
                self.vars_to_remove.add(var_name)
                return None

        return self.generic_visit(node)

    def visit_Expr(self, node):
        # Replace .pop(0) with .popleft()
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
                self.imports_needed.add("from collections import deque")
        return self.generic_visit(node)

    def visit_If(self, node):
        # Inject _name_set = set(name) and rewrite if x in name → if x in _name_set
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            collection = node.test.comparators[0]
            if isinstance(collection, ast.Name):
                list_var = collection.id
                temp_var = f"_{list_var}_set"
                fix_code = f"{temp_var} = set({list_var})"
                self.fixes.append(FixPlan(node=None, replacement_code=fix_code))
                node.test.comparators[0] = ast.Name(id=temp_var, ctx=ast.Load())
        return self.generic_visit(node)

    def apply_fixes(self, tree):
        # Inject top-level fixes (e.g. set(), Counter()) only once
        injected_nodes = []
        for plan in self.fixes:
            if plan.node is None:
                injected_nodes.extend(ast.parse(plan.replacement_code).body)

        tree.body = injected_nodes + tree.body

        # Apply node replacements only where a specific node exists
        for plan in self.fixes:
            if plan.node is not None:
                tree = self.replace_node(tree, plan.node, ast.parse(plan.replacement_code).body)

        return tree

    def replace_node(self, tree, old_node, new_nodes):
        class NodeReplacer(ast.NodeTransformer):
            def __init__(self, old_node, new_nodes):
                self.old_node = old_node
                self.new_nodes = new_nodes

            def visit_Module(self, node):
                new_body = []
                for stmt in node.body:
                    if stmt == self.old_node:
                        new_body.extend(new_nodes)
                    else:
                        new_body.append(stmt)
                node.body = new_body
                return node

        replacer = NodeReplacer(old_node, new_nodes)
        return replacer.visit(tree)

def apply_auto_fixes(code):
    tree = ast.parse(code)
    fixer = AutoFixer()
    tree = fixer.visit(tree)        # collect fixes + detect patterns
    tree = fixer.apply_fixes(tree)  # apply changes

    fixed_code = astor.to_source(tree)

    imports = {fix.import_line for fix in fixer.fixes if fix.import_line}
    imports.update(fixer.imports_needed)
    import_lines = "\n".join(sorted(filter(None, imports))) + "\n" if imports else ""

    return import_lines + fixed_code, bool(fixer.fixes or fixer.imports_needed)
