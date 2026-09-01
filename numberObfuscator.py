import ast
import re


def obfuscate_numbers_in_file(filepath):
    """Обрабатывает файл, заменяя числа на их бинарное представление"""

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    # Функция для замены чисел в строке
    def replace_numbers(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            if num >= 0 and num <= 1000000:  # Ограничим диапазон для безопасности
                return f"int('0b{bin(num)[2:]}', 0)"
            return num_str
        except ValueError:
            return num_str

    # Регулярное выражение для поиска чисел
    # Игнорируем числа внутри строк и комментариев
    lines = source.split('\n')
    new_lines = []

    in_string = False
    string_char = None
    escape_next = False

    for line in lines:
        # Проверяем, не находится ли строка в комментарии или строке
        if '#' in line and not in_string:
            # Разделяем на код и комментарий
            code_part, comment_part = line.split('#', 1)
            # Обрабатываем только код
            code_part = re.sub(r'(?<![a-zA-Z0-9_.])-?\d+(?![a-zA-Z0-9_.])', replace_numbers, code_part)
            new_lines.append(code_part + '#' + comment_part)
        else:
            # Обрабатываем всю строку
            new_line = re.sub(r'(?<![a-zA-Z0-9_.])-?\d+(?![a-zA-Z0-9_.])', replace_numbers, line)
            new_lines.append(new_line)

    new_source = '\n'.join(new_lines)

    # Проверяем, что код валидный после замены
    try:
        ast.parse(new_source)
    except SyntaxError:
        print(f"  Предупреждение: Обработка чисел в {filepath} вызвала синтаксическую ошибку. Используем AST-подход.")
        # Пробуем через AST
        try:
            tree = ast.parse(source)

            class NumberTransformer(ast.NodeTransformer):
                def visit_Num(self, node):
                    if isinstance(node.n, int) and node.n >= 0:
                        return ast.Call(
                            func=ast.Name(id='int', ctx=ast.Load()),
                            args=[ast.Constant(value=f'0b{bin(node.n)[2:]}'), ast.Constant(value=0)],
                            keywords=[]
                        )
                    return node

                def visit_Constant(self, node):
                    if isinstance(node.value, int) and node.value >= 0:
                        return ast.Call(
                            func=ast.Name(id='int', ctx=ast.Load()),
                            args=[ast.Constant(value=f'0b{bin(node.value)[2:]}'), ast.Constant(value=0)],
                            keywords=[]
                        )
                    return node

            new_tree = NumberTransformer().visit(tree)
            ast.fix_missing_locations(new_tree)
            new_source = ast.unparse(new_tree)
        except Exception as e:
            print(f"  Ошибка при обработке чисел в {filepath}: {e}")
            return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_source)

    return True