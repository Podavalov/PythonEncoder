import os
import shutil
from fileCollector import collect_py_files as coll
from variableReceiver import get_names_from_script as get_names
from randomNameGenerator import create_rename_mapping as cr
from renameEngine import rename_identifiers_in_file

def extract_all_names(data_dict):
    if 'all_definitions' in data_dict:
        return data_dict['all_definitions']
    names = []
    names.extend(data_dict.get('variables', []))
    names.extend(data_dict.get('functions', []))
    classes = data_dict.get('classes', {})
    if isinstance(classes, dict):
        names.extend(classes.keys())
        for methods in classes.values():
            names.extend(methods)
    else:
        names.extend(classes)
    names.extend(data_dict.get('methods', []))
    return names

if __name__ == "__main__":
    target = input("Введите путь к директории: ").strip()
    if not os.path.isdir(target):
        print("Указанная директория не существует.")
        exit(1)


    parent_dir = os.path.dirname(target)
    base_name = os.path.basename(target)
    copy_dir = os.path.join(parent_dir, base_name + "_obfuscated")

    # Если такая уже есть – добавляем номер
    if os.path.exists(copy_dir):
        i = 1
        while os.path.exists(os.path.join(parent_dir, f"{base_name}_copy_{i}")):
            i += 1
        copy_dir = os.path.join(parent_dir, f"{base_name}_copy_{i}")

    print(f"Создаю копию директории: {copy_dir}")
    shutil.copytree(target, copy_dir, ignore_dangling_symlinks=True)

    # Собираем файлы в копии
    py_files = coll(copy_dir)
    print(f"Найдено .py-файлов: {len(py_files)}")

    # Собираем все имена определений
    all_names = set()
    for file in py_files:
        data = get_names(file)
        names = extract_all_names(data)
        all_names.update(names)

    # Фильтруем встроенные и стандартные
    builtins = set(dir(__builtins__))
    all_names = all_names - builtins
    common_modules = {'os', 'sys', 're', 'json', 'shutil', 'pathlib', 'random', 'string', 'ast'}
    all_names = all_names - common_modules

    print(f"Уникальных имён для замены: {len(all_names)}")


    print("Примеры имён для замены (первые 10):", list(all_names)[:10])

    if not all_names:
        print("Нет имён для замены. Завершение.")
        exit(0)

    rename_dict = cr(all_names, name_length=15)
    print(f"Сгенерировано {len(rename_dict)} пар замен.")

    # Применяем замены
    for file in py_files:
        print(f"  Обработка: {file}")
        success = rename_identifiers_in_file(file, rename_dict)
        if success:
            print("    ✓ Замены выполнены")
        else:
            print("    ✗ Ошибка (синтаксическая)")

    print("\nГотово! Все изменения применены к копии директории:")
    print(copy_dir)
    print("Оригинальная директория не изменена.")