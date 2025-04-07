# auto_fixer.py

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

    def visit_Assign(self, node):
        # Match pattern: d[key] = d.get(key, 0) + 1 → Counter
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
                fix_code = f"{var_name} = Counter()\n{var_name}.update(your_data_here)"
                plan = FixPlan(node, fix_code, import_line="from collections import Counter")
                self.fixes.append(plan)

        return self.generic_visit(node)

    def visit_Expr(self, node):
        # Match: queue.pop(0) → queue.popleft()
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "pop":
                if len(call.args) == 1 and isinstance(call.args[0], ast.Constant) and call.args[0].value == 0:
                    call.func.attr = "popleft"
                    call.args = []
                    self.imports_needed.add("from collections import deque")
        return self.generic_visit(node)

    def apply_fixes(self, tree):
        for plan in self.fixes:
            new_nodes = ast.parse(plan.replacement_code).body
            tree = self.replace_node(tree, plan.node, new_nodes)
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
                        new_body.extend(self.new_nodes)
                    else:
                        new_body.append(stmt)
                node.body = new_body
                return node

        replacer = NodeReplacer(old_node, new_nodes)
        return replacer.visit(tree)

def apply_auto_fixes(code):
    tree = ast.parse(code)
    fixer = AutoFixer()
    fixer.visit(tree)
    tree = fixer.apply_fixes(tree)
    fixed_code = astor.to_source(tree)

    import_lines = ""
    # Avoid duplicate imports
    imports = {plan.import_line for plan in fixer.fixes if plan.import_line}
    imports.update(fixer.imports_needed)

    if imports:
        import_lines = "\n".join(sorted(imports)) + "\n"

    return import_lines + fixed_code, bool(fixer.fixes or fixer.imports_needed)
