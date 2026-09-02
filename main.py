import os
import shutil
import argparse
import secrets
from fileCollector import collect_py_files as coll
from encoder import protect, machine_code

def get_user_input(prompt, default=None, is_bool=False):
    """Вспомогательная функция для интерактивного ввода."""
    if default is not None:
        prompt = f"{prompt} (по умолчанию: {default}): "
    else:
        prompt = f"{prompt}: "
    value = input(prompt).strip()
    if not value and default is not None:
        return default
    if is_bool:
        return value.lower() in ('y', 'yes', 'true', '1')
    return value

def main():
    parser = argparse.ArgumentParser(
        description="Пакетная защита Python-файлов в директории с помощью PythonEncoder."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        help="Путь к директории с исходными .py файлами"
    )
    parser.add_argument(
        "--key",
        help="Общий ключ для всех файлов (если не указан, будет сгенерирован)"
    )
    parser.add_argument(
        "--machine",
        default="any",
        help="Привязка к машине: any, auto или код машины (по умолчанию any)"
    )
    parser.add_argument(
        "--expire-days",
        type=int,
        default=0,
        help="Срок действия в днях (0 — бессрочно)"
    )
    parser.add_argument(
        "--no-machine",
        action="store_true",
        help="Отключить привязку к машине (то же, что --machine any)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Запросить параметры интерактивно (если не заданы через аргументы)"
    )

    args = parser.parse_args()

    # Определяем директорию
    if args.directory:
        target = args.directory
    else:
        target = get_user_input("Введите путь к директории", default=None)
        if not target:
            print("Директория не указана. Завершение.")
            return

    if not os.path.isdir(target):
        print(f"Ошибка: директория '{target}' не существует.")
        return

    # Интерактивный режим, если запрошен или если аргументы не заданы явно
    if args.interactive or (not args.key and not args.machine and not args.expire_days and not args.no_machine):
        # Если ключ не передан, предложим ввести или сгенерировать
        if not args.key:
            key_input = get_user_input("Введите ключ (оставьте пустым для генерации)", default="")
            args.key = key_input if key_input else None
        # Параметры машины
        if not args.no_machine:
            machine_choice = get_user_input("Привязка к машине (any/auto/код, по умолчанию any)", default="any")
            args.machine = machine_choice
        else:
            args.machine = "any"
        # Срок
        if not args.expire_days:
            days_input = get_user_input("Срок действия в днях (0 - бессрочно)", default="0")
            try:
                args.expire_days = int(days_input) if days_input else 0
            except ValueError:
                args.expire_days = 0

    # Если ключ не указан, генерируем общий для всех файлов
    if args.key is None:
        args.key = secrets.token_hex(32)
        print(f"Сгенерирован общий ключ: {args.key}")

    # Привязка к машине
    if args.no_machine:
        machine = "any"
    elif args.machine.lower() == "auto":
        machine = machine_code()
        print(f"Код текущей машины: {machine}")
    else:
        machine = args.machine

    # Создаём копию директории
    parent_dir = os.path.dirname(target)
    base_name = os.path.basename(target)
    copy_dir = os.path.join(parent_dir, base_name + "_encrypted")
    if os.path.exists(copy_dir):
        i = 1
        while os.path.exists(os.path.join(parent_dir, f"{base_name}_encrypted{i}")):
            i += 1
        copy_dir = os.path.join(parent_dir, f"{base_name}_encrypted{i}")
    print(f"Создаю копию директории: {copy_dir}")
    shutil.copytree(target, copy_dir, ignore_dangling_symlinks=True)

    # Собираем все .py файлы в копии
    py_files = coll(copy_dir)
    print(f"Найдено .py-файлов: {len(py_files)}")

    # Защищаем каждый файл
    for file in py_files:
        print(f"Шифрование {file} началось")
        try:
            protect(
                input_path=file,
                output_path=file,          # перезаписываем файл в копии
                key=args.key,
                machine=machine,
                expire_days=args.expire_days if args.expire_days > 0 else None
            )
            print(f"{file} успешно зашифрован")
        except Exception as e:
            print(f"Ошибка при шифровании {file}: {e}")

    print("\nГотово! Все изменения применены к копии директории:")
    print(copy_dir)
    print("Оригинальная директория не изменена.")

if __name__ == "__main__":
    main()