import ast

def rename_identifiers_in_file(filepath, rename_map):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  Пропуск {filepath} — синтаксическая ошибка: {e}")
        return False

    class RenameTransformer(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in rename_map:
                node.id = rename_map[node.id]
            return node

        def visit_Attribute(self, node):
            if node.attr in rename_map:
                node.attr = rename_map[node.attr]
            self.generic_visit(node)
            return node

        def visit_FunctionDef(self, node):
            if node.name in rename_map:
                node.name = rename_map[node.name]
            self.generic_visit(node)
            return node

        def visit_ClassDef(self, node):
            if node.name in rename_map:
                node.name = rename_map[node.name]
            self.generic_visit(node)
            return node

        def visit_arg(self, node):
            if node.arg in rename_map:
                node.arg = rename_map[node.arg]
            return node

        def visit_ExceptHandler(self, node):
            if node.name and node.name in rename_map:
                node.name = rename_map[node.name]
            self.generic_visit(node)
            return node


        def visit_Import(self, node):
            for alias in node.names:
                if alias.name in rename_map:
                    alias.name = rename_map[alias.name]
                if alias.asname and alias.asname in rename_map:
                    alias.asname = rename_map[alias.asname]
            self.generic_visit(node)
            return node

        def visit_ImportFrom(self, node):
            for alias in node.names:
                if alias.name in rename_map:
                    alias.name = rename_map[alias.name]
                if alias.asname and alias.asname in rename_map:
                    alias.asname = rename_map[alias.asname]
            self.generic_visit(node)
            return node

    new_tree = RenameTransformer().visit(tree)
    ast.fix_missing_locations(new_tree)

    try:
        new_source = ast.unparse(new_tree)
    except AttributeError:
        print(f"  Ошибка: ast.unparse недоступен. Требуется Python 3.9+.")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_source)

    return True