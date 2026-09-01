import ast
import re


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

        def visit_Num(self, node):
            # Заменяем числа на их бинарное представление
            if isinstance(node.n, int) and node.n >= 0:
                binary_str = bin(node.n)[2:]  # убираем '0b'
                return ast.Call(
                    func=ast.Name(id='int', ctx=ast.Load()),
                    args=[ast.Constant(value=f'0b{binary_str}'), ast.Constant(value=0)],
                    keywords=[]
                )
            return node

        def visit_Constant(self, node):
            # Для Python 3.8+ числа хранятся в Constant
            if isinstance(node.value, int) and node.value >= 0:
                binary_str = bin(node.value)[2:]
                return ast.Call(
                    func=ast.Name(id='int', ctx=ast.Load()),
                    args=[ast.Constant(value=f'0b{binary_str}'), ast.Constant(value=0)],
                    keywords=[]
                )
            return node

    new_tree = RenameTransformer().visit(tree)
    ast.fix_missing_locations(new_tree)

    try:
        new_source = ast.unparse(new_tree)
    except AttributeError:
        print(f"  Ошибка: ast.unparse недоступен. Требуется Python 3.9+.")
        return False

    # Дополнительная обработка для чисел в строковом виде (например, в f-строках)
    # Это нужно, потому что ast не всегда корректно обрабатывает числа в сложных выражениях
    def replace_numbers_in_code(code):
        # Заменяем числа, которые не являются частью других чисел или идентификаторов
        # Используем lookbehind/lookahead, чтобы не заменять числа в словах
        pattern = r'(?<![a-zA-Z0-9_])-?\d+(?![a-zA-Z0-9_])'

        def replace_match(match):
            num_str = match.group(0)
            if num_str.startswith('-'):
                # Отрицательные числа оставляем как есть или можно обработать отдельно
                return num_str
            try:
                num = int(num_str)
                if num >= 0:
                    return f"int('0b{bin(num)[2:]}', 0)"
                return num_str
            except ValueError:
                return num_str

        return re.sub(pattern, replace_match, code)

    # Применяем дополнительную обработку
    new_source = replace_numbers_in_code(new_source)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_source)

    return True