import random
import string

def generate_random_name(length=10):
    first_char = random.choice(string.ascii_letters)  # или можно добавить '_'
    other_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))
    return first_char + other_chars

def create_rename_mapping(old_names, name_length=10):
    """
    Принимает множество или список старых имён.
    Возвращает словарь {old_name: new_name} со случайными уникальными именами.
    """
    mapping = {}
    used_new_names = set()

    for old in old_names:
        # Генерируем новое имя, пока не получим уникальное
        while True:
            new_name = generate_random_name(name_length)
            if new_name not in used_new_names:
                used_new_names.add(new_name)
                mapping[old] = new_name
                break

    return mapping