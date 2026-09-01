import ast
import struct
from decimal import Decimal


def float_to_binary_representation(value):
    """Преобразует float в бинарное представление через struct"""
    if isinstance(value, float):
        # Преобразуем float в 64-битный binary
        packed = struct.pack('>d', value)
        # Получаем битовое представление
        bits = int.from_bytes(packed, byteorder='big')
        binary_str = bin(bits)[2:].zfill(64)
        # Возвращаем как шестнадцатеричную строку для компактности
        hex_str = hex(bits)[2:].zfill(16)
        return f"struct.unpack('>d', bytes.fromhex('{hex_str}'))[0]"
    return None


def decimal_to_binary_representation(value):
    """Преобразует Decimal в бинарное представление"""
    if isinstance(value, Decimal):
        # Получаем битовое представление Decimal
        # Используем представление в виде строки и преобразуем в бинарный вид
        decimal_str = str(value)
        # Кодируем строку в байты и преобразуем в бинарный вид
        bytes_repr = decimal_str.encode('utf-8')
        hex_str = bytes_repr.hex()
        return f"decimal.Decimal(bytes.fromhex('{hex_str}').decode('utf-8'))"
    return None


def obfuscate_numbers_in_file(filepath):
    """Обрабатывает файл, заменяя числа на их бинарное представление"""

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    def replace_number(match):
        num_str = match.group(0)

        # Проверяем, не является ли число частью идентификатора
        start, end = match.span()
        prev_char = source[start - 1] if start > 0 else ''
        next_char = source[end] if end < len(source) else ''

        if (prev_char.isalnum() or prev_char == '_' or
                next_char.isalnum() or next_char == '_'):
            return num_str

        try:
            # Пробуем преобразовать в float
            if '.' in num_str or 'e' in num_str.lower():
                value = float(num_str)
                if value.is_integer():
                    # Целое число, но в float формате (например, 5.0)
                    int_val = int(value)
                    if int_val >= 0:
                        return f"float(int('0b{bin(int_val)[2:]}', 0))"
                    else:
                        return f"float(-int('0b{bin(abs(int_val))[2:]}', 0))"
                else:
                    # Действительное число с плавающей точкой
                    return float_to_binary_representation(value)
            else:
                # Целое число
                value = int(num_str)
                if value >= 0:
                    return f"int('0b{bin(value)[2:]}', 0)"
                else:
                    return f"-int('0b{bin(abs(value))[2:]}', 0)"
        except (ValueError, OverflowError):
            return num_str

    # Обрабатываем строку, учитывая строковые литералы и комментарии
    def process_line(line):
        result = []
        i = 0
        in_string = False
        string_char = None
        escape_next = False
        in_comment = False

        while i < len(line):
            char = line[i]

            # Проверяем начало комментария (вне строк)
            if not in_string and char == '#':
                in_comment = True
                result.append(char)
                i += 1
                # Добавляем остаток строки без изменений
                result.append(line[i:])
                break

            # Обработка строковых литералов
            if not in_string and char in '"\'':
                in_string = True
                string_char = char
                result.append(char)
                i += 1
                continue

            if in_string:
                if escape_next:
                    result.append(char)
                    escape_next = False
                    i += 1
                    continue

                if char == '\\':
                    escape_next = True
                    result.append(char)
                    i += 1
                    continue

                if char == string_char:
                    in_string = False
                    string_char = None
                    result.append(char)
                    i += 1
                    continue

                result.append(char)
                i += 1
                continue

            # Обработка чисел вне строк и комментариев
            if not in_string and not in_comment:
                # Проверяем, начинается ли здесь число
                if char.isdigit() or (char == '-' and i + 1 < len(line) and line[i + 1].isdigit()):
                    # Находим конец числа
                    j = i
                    if char == '-':
                        j += 1

                    while j < len(line) and (line[j].isdigit() or line[j] == '.' or line[j].lower() in 'ej'):
                        j += 1

                    num_str = line[i:j]
                    # Проверяем, что это действительно число, а не часть слова
                    prev_ok = i == 0 or not (line[i - 1].isalnum() or line[i - 1] == '_')
                    next_ok = j == len(line) or not (line[j].isalnum() or line[j] == '_') if j < len(line) else True

                    if prev_ok and next_ok:
                        try:
                            # Пробуем преобразовать
                            if '.' in num_str or 'e' in num_str.lower():
                                value = float(num_str)
                                if value.is_integer():
                                    int_val = int(value)
                                    if int_val >= 0:
                                        result.append(f"float(int('0b{bin(int_val)[2:]}', 0))")
                                    else:
                                        result.append(f"float(-int('0b{bin(abs(int_val))[2:]}', 0))")
                                else:
                                    result.append(float_to_binary_representation(value) or num_str)
                            else:
                                value = int(num_str)
                                if value >= 0:
                                    result.append(f"int('0b{bin(value)[2:]}', 0)")
                                else:
                                    result.append(f"-int('0b{bin(abs(value))[2:]}', 0)")
                        except (ValueError, OverflowError):
                            result.append(num_str)

                        i = j
                        continue
                    else:
                        result.append(char)
                        i += 1
                        continue
                else:
                    result.append(char)
                    i += 1
            else:
                result.append(char)
                i += 1

        return ''.join(result)

    # Обрабатываем файл построчно
    lines = source.split('\n')
    new_lines = []

    for line in lines:
        new_lines.append(process_line(line))

    new_source = '\n'.join(new_lines)

    # Проверяем валидность кода
    try:
        ast.parse(new_source)
    except SyntaxError:
        print(f"  Предупреждение: Обработка чисел в {filepath} вызвала синтаксическую ошибку. Используем AST-подход.")

        # Пробуем через AST с поддержкой float
        try:
            import decimal

            class NumberTransformer(ast.NodeTransformer):
                def visit_Num(self, node):
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
                        # Используем struct для float
                        import struct
                        packed = struct.pack('>d', node.n)
                        bits = int.from_bytes(packed, byteorder='big')
                        hex_str = hex(bits)[2:].zfill(16)

                        # Создаем выражение: struct.unpack('>d', bytes.fromhex('...'))[0]
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
                        import struct
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

            # Добавляем импорт struct, если его нет
            tree = ast.parse(new_source)

            # Проверяем, есть ли импорт struct
            has_struct_import = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == 'struct':
                            has_struct_import = True
                            break
                elif isinstance(node, ast.ImportFrom):
                    if node.module == 'struct':
                        has_struct_import = True
                        break

            # Добавляем импорт struct в начало, если он не обнаружен
            if not has_struct_import:
                import_node = ast.Import(names=[ast.alias(name='struct', asname=None)])
                if isinstance(tree, ast.Module):
                    tree.body.insert(0, import_node)

            new_tree = NumberTransformer().visit(tree)
            ast.fix_missing_locations(new_tree)
            new_source = ast.unparse(new_tree)

        except Exception as e:
            print(f"  Ошибка при обработке чисел в {filepath}: {e}")
            return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_source)

    return True