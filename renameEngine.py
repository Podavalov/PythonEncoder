import ast
import struct


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
            # Обработка чисел через AST
            if isinstance(node.n, int):
                if node.n >= 0:
                    return ast.Call(
                        func=ast.Name(id='int', ctx=ast.Load()),
                        args=[ast.Constant(value=f'0b{bin(node.n)[2:]}'), ast.Constant(value=0)],
                        keywords=[]
                    )
                else:
                    return ast.UnaryOp(
                        op=ast.USub(),
                        operand=ast.Call(
                            func=ast.Name(id='int', ctx=ast.Load()),
                            args=[ast.Constant(value=f'0b{bin(abs(node.n))[2:]}'), ast.Constant(value=0)],
                            keywords=[]
                        )
                    )
            elif isinstance(node.n, float):
                # Преобразуем float в бинарное представление через struct
                packed = struct.pack('>d', node.n)
                bits = int.from_bytes(packed, byteorder='big')
                hex_str = hex(bits)[2:].zfill(16)

                # Проверяем, есть ли импорт struct
                # Добавим его позже, если необходимо
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='struct', ctx=ast.Load()),
                                attr='unpack',
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Constant(value='>d'),
                                ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id='bytes', ctx=ast.Load()),
                                        attr='fromhex',
                                        ctx=ast.Load()
                                    ),
                                    args=[ast.Constant(value=hex_str)],
                                    keywords=[]
                                )
                            ],
                            keywords=[]
                        ),
                        attr='__getitem__',
                        ctx=ast.Load()
                    ),
                    args=[ast.Constant(value=0)],
                    keywords=[]
                )
            return node

        def visit_Constant(self, node):
            # Для Python 3.8+
            if isinstance(node.value, int):
                if node.value >= 0:
                    return ast.Call(
                        func=ast.Name(id='int', ctx=ast.Load()),
                        args=[ast.Constant(value=f'0b{bin(node.value)[2:]}'), ast.Constant(value=0)],
                        keywords=[]
                    )
                else:
                    return ast.UnaryOp(
                        op=ast.USub(),
                        operand=ast.Call(
                            func=ast.Name(id='int', ctx=ast.Load()),
                            args=[ast.Constant(value=f'0b{bin(abs(node.value))[2:]}'), ast.Constant(value=0)],
                            keywords=[]
                        )
                    )
            elif isinstance(node.value, float):
                # Преобразуем float в бинарное представление через struct
                packed = struct.pack('>d', node.value)
                bits = int.from_bytes(packed, byteorder='big')
                hex_str = hex(bits)[2:].zfill(16)

                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id='struct', ctx=ast.Load()),
                                attr='unpack',
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Constant(value='>d'),
                                ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id='bytes', ctx=ast.Load()),
                                        attr='fromhex',
                                        ctx=ast.Load()
                                    ),
                                    args=[ast.Constant(value=hex_str)],
                                    keywords=[]
                                )
                            ],
                            keywords=[]
                        ),
                        attr='__getitem__',
                        ctx=ast.Load()
                    ),
                    args=[ast.Constant(value=0)],
                    keywords=[]
                )
            return node

    new_tree = RenameTransformer().visit(tree)
    ast.fix_missing_locations(new_tree)

    # Добавляем импорт struct, если есть float числа и он еще не импортирован
    has_struct_import = False
    has_float_numbers = False

    for node in ast.walk(new_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'struct':
                    has_struct_import = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == 'struct':
                has_struct_import = True
        elif isinstance(node, ast.Call):
            # Проверяем, есть ли вызов struct.unpack
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'struct':
                    has_float_numbers = True
                elif isinstance(node.func.value, ast.Call):
                    if isinstance(node.func.value.func, ast.Attribute):
                        if isinstance(node.func.value.func.value,
                                      ast.Name) and node.func.value.func.value.id == 'struct':
                            has_float_numbers = True

    if has_float_numbers and not has_struct_import:
        import_node = ast.Import(names=[ast.alias(name='struct', asname=None)])
        if isinstance(new_tree, ast.Module):
            new_tree.body.insert(0, import_node)

    try:
        new_source = ast.unparse(new_tree)
    except AttributeError:
        print(f"  Ошибка: ast.unparse недоступен. Требуется Python 3.9+.")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_source)

    return True