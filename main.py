import os
import shutil
import argparse
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path
from fileCollector import collect_py_files as coll, EXCLUDED_PATTERNS, add_exclusion
from encoder import protect, machine_code


def get_user_input(prompt, default=None, required=False, validator=None):
    """
    Вспомогательная функция для интерактивного ввода с валидацией.

    Args:
        prompt: Текст подсказки
        default: Значение по умолчанию
        required: Обязательно ли вводить значение
        validator: Функция-валидатор, возвращает (bool, сообщение об ошибке)
    """
    while True:
        if default is not None:
            full_prompt = f"{prompt} (по умолчанию: {default}): "
        else:
            full_prompt = f"{prompt}: "

        value = input(full_prompt).strip()

        if not value and default is not None:
            value = default
        elif not value and required:
            print("⚠️ Это поле обязательно для заполнения!")
            continue

        if validator:
            is_valid, error_msg = validator(value)
            if not is_valid:
                print(f"❌ {error_msg}")
                continue

        return value


def validate_key(key):
    """Проверка ключа."""
    if key == "":
        return True, "OK"
    if len(key) < 8:
        return False, "Ключ должен быть минимум 8 символов"
    return True, "OK"


def validate_days(days_str):
    """Проверка срока действия."""
    try:
        days = int(days_str)
        if days < 0:
            return False, "Дни не могут быть отрицательными"
        return True, "OK"
    except ValueError:
        return False, "Введите целое число"


def validate_machine(machine):
    """Проверка привязки к машине."""
    if machine.lower() in ['any', 'auto']:
        return True, "OK"
    if len(machine) == 16 and all(c in '0123456789abcdef' for c in machine.lower()):
        return True, "OK"
    return False, "Введите 'any', 'auto' или 16-символьный код машины"


def choose_interactive_mode():
    """Интерактивный выбор режима работы."""
    print("\n" + "=" * 60)
    print("🔐 PythonEncoder - Пакетная защита")
    print("=" * 60)

    modes = {
        "1": {"name": "Быстрый старт", "desc": "Сгенерировать ключ, без привязки, бессрочно"},
        "2": {"name": "Ручная настройка", "desc": "Указать все параметры вручную"},
        "3": {"name": "Продвинутый", "desc": "Полный контроль с проверками"}
    }

    print("\nВыберите режим:")
    for key, mode in modes.items():
        print(f"  {key}. {mode['name']} - {mode['desc']}")

    choice = get_user_input("Ваш выбор", default="1")
    return choice


def interactive_advanced_config():
    """Продвинутая интерактивная настройка."""
    print("\n" + "=" * 60)
    print("⚙️  Продвинутая настройка")
    print("=" * 60)

    # 1. Ключ
    print("\n🔑 Настройка ключа:")
    print("  [1] Сгенерировать случайный ключ")
    print("  [2] Ввести свой ключ")
    key_choice = get_user_input("Выберите вариант", default="1")

    if key_choice == "2":
        key = get_user_input(
            "Введите ключ (минимум 8 символов)",
            required=True,
            validator=validate_key
        )
        print(f"✅ Использую ключ: {key[:4]}...{key[-4:]}")
    else:
        key = secrets.token_hex(32)
        print(f"✅ Сгенерирован случайный ключ: {key}")

    # 2. Привязка к машине
    print("\n💻 Настройка привязки к машине:")
    print("  [1] Без привязки (можно запускать где угодно)")
    print("  [2] Привязать к текущей машине")
    print("  [3] Ввести код машины вручную")
    machine_choice = get_user_input("Выберите вариант", default="1")

    if machine_choice == "1":
        machine = "any"
        print("✅ Без привязки к машине")
    elif machine_choice == "2":
        machine = "auto"
        code = machine_code()
        print(f"✅ Привязано к текущей машине (код: {code})")
    else:
        machine = get_user_input(
            "Введите код машины (16 символов)",
            required=True,
            validator=validate_machine
        )
        print(f"✅ Привязано к машине: {machine}")

    # 3. Срок действия
    print("\n⏰ Настройка срока действия:")
    print("  [1] Бессрочно")
    print("  [2] 30 дней")
    print("  [3] 90 дней")
    print("  [4] 365 дней (1 год)")
    print("  [5] Свой срок")
    days_choice = get_user_input("Выберите вариант", default="1")

    days_map = {
        "1": 0,
        "2": 30,
        "3": 90,
        "4": 365,
    }

    if days_choice in days_map:
        expire_days = days_map[days_choice]
        if expire_days == 0:
            print("✅ Бессрочный доступ")
        else:
            expire_date = datetime.now() + timedelta(days=expire_days)
            print(f"✅ Срок действия до: {expire_date.strftime('%d.%m.%Y')} ({expire_days} дней)")
    else:
        expire_days = int(get_user_input(
            "Введите количество дней",
            required=True,
            validator=validate_days
        ))
        if expire_days == 0:
            print("✅ Бессрочный доступ")
        else:
            expire_date = datetime.now() + timedelta(days=expire_days)
            print(f"✅ Срок действия до: {expire_date.strftime('%d.%m.%Y')} ({expire_days} дней)")

    # 4. Исключения
    print("\n📁 Настройка исключений:")
    print("  [1] Использовать стандартные исключения")
    print("  [2] Добавить свои исключения")
    exclude_choice = get_user_input("Выберите вариант", default="1")

    extra_excludes = []
    if exclude_choice == "2":
        print("\nВведите файлы/шаблоны для исключения (по одному)")
        print("Для завершения введите пустую строку")
        print(f"Текущие исключения: {', '.join(EXCLUDED_PATTERNS[:5])}...")
        while True:
            pattern = get_user_input("Шаблон исключения", default="")
            if not pattern:
                break
            extra_excludes.append(pattern)
            print(f"  ➕ Добавлено: {pattern}")

    return {
        'key': key,
        'machine': machine,
        'expire_days': expire_days,
        'excludes': extra_excludes
    }


def print_summary(config):
    """Печать сводки настроек."""
    print("\n" + "=" * 60)
    print("📋 Сводка настроек")
    print("=" * 60)
    print(f"🔑 Ключ: {config['key'][:8]}...{config['key'][-8:]}")
    print(f"💻 Привязка: {config['machine']}")
    if config['expire_days'] > 0:
        expire_date = datetime.now() + timedelta(days=config['expire_days'])
        print(f"⏰ Срок: {expire_date.strftime('%d.%m.%Y')} ({config['expire_days']} дней)")
    else:
        print("⏰ Срок: Бессрочно")
    if config['excludes']:
        print(f"📁 Исключения: {', '.join(config['excludes'])}")
    print("=" * 60)

    confirm = get_user_input("Продолжить с этими настройками? (y/n)", default="y")
    return confirm.lower() in ['y', 'yes', 'да']


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
        default=None,
        help="Привязка к машине: any, auto или код машины"
    )
    parser.add_argument(
        "--expire-days",
        type=int,
        default=None,
        help="Срок действия в днях (0 — бессрочно)"
    )
    parser.add_argument(
        "--no-machine",
        action="store_true",
        help="Отключить привязку к машине (то же, что --machine any)"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Дополнительные файлы/шаблоны для исключения"
    )
    parser.add_argument(
        "--show-excluded",
        action="store_true",
        help="Показать список исключаемых файлов"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Запросить параметры интерактивно"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Быстрый режим: сгенерировать ключ, без привязки, бессрочно"
    )

    args = parser.parse_args()

    # Показать список исключений
    if args.show_excluded:
        print("📁 Файлы, которые НЕ будут шифроваться:")
        for pattern in EXCLUDED_PATTERNS:
            print(f"  - {pattern}")
        return

    # Определяем директорию
    if args.directory:
        target = args.directory
    else:
        target = get_user_input("📁 Введите путь к директории", required=True)
        if not target:
            print("❌ Директория не указана. Завершение.")
            return

    if not os.path.isdir(target):
        print(f"❌ Ошибка: директория '{target}' не существует.")
        return

    # Конфигурация
    config = {
        'key': args.key,
        'machine': args.machine or ("any" if args.no_machine else None),
        'expire_days': args.expire_days if args.expire_days is not None else 0,
        'excludes': args.exclude or []
    }

    # Интерактивный режим или выбор режима
    if args.interactive:
        mode = choose_interactive_mode()

        if mode == "1":  # Быстрый старт
            config['key'] = secrets.token_hex(32)
            config['machine'] = "any"
            config['expire_days'] = 0
            print(f"\n✅ Сгенерирован ключ: {config['key']}")
            print("✅ Без привязки к машине")
            print("✅ Бессрочный доступ")

        elif mode == "2":  # Ручная настройка
            config = interactive_advanced_config()
            # Добавляем исключения из интерактивного режима
            if config.get('excludes'):
                for pattern in config['excludes']:
                    add_exclusion(pattern)

        elif mode == "3":  # Продвинутый
            config = interactive_advanced_config()
            if config.get('excludes'):
                for pattern in config['excludes']:
                    add_exclusion(pattern)

        # Показываем сводку
        if not print_summary(config):
            print("❌ Отменено пользователем")
            return

    # Быстрый режим через аргументы
    elif args.quick:
        config['key'] = secrets.token_hex(32)
        config['machine'] = "any"
        config['expire_days'] = 0
        print(f"\n🚀 Быстрый режим")
        print(f"🔑 Ключ: {config['key']}")
        print("✅ Без привязки к машине")
        print("✅ Бессрочный доступ")

    # Если ключ не указан и не интерактивный режим
    elif config['key'] is None:
        config['key'] = secrets.token_hex(32)
        print(f"\n🔑 Сгенерирован случайный ключ: {config['key']}")

    # Если машина не указана
    if config['machine'] is None:
        config['machine'] = "any"
        print("💻 Без привязки к машине")

    # Автоматическая привязка
    if config['machine'] == "auto":
        config['machine'] = machine_code()
        print(f"💻 Привязано к текущей машине: {config['machine']}")

    # Добавляем пользовательские исключения
    if config.get('excludes'):
        for pattern in config['excludes']:
            add_exclusion(pattern)
            print(f"📁 Добавлено исключение: {pattern}")

    # Показываем список исключений
    print("\n📁 Файлы, которые НЕ будут зашифрованы:")
    for pattern in EXCLUDED_PATTERNS:
        print(f"  - {pattern}")

    # Создаём копию директории
    parent_dir = os.path.dirname(target)
    base_name = os.path.basename(target)
    copy_dir = os.path.join(parent_dir, base_name + "_encrypted")
    if os.path.exists(copy_dir):
        i = 1
        while os.path.exists(os.path.join(parent_dir, f"{base_name}_encrypted{i}")):
            i += 1
        copy_dir = os.path.join(parent_dir, f"{base_name}_encrypted{i}")

    print(f"\n📂 Создаю копию директории: {copy_dir}")
    try:
        shutil.copytree(target, copy_dir, ignore_dangling_symlinks=True)
    except Exception as e:
        print(f"❌ Ошибка при копировании: {e}")
        return

    # Собираем .py файлы
    py_files = coll(copy_dir)
    print(f"📄 Найдено .py-файлов для обработки: {len(py_files)}")

    if not py_files:
        print("⚠️ Нет файлов для обработки")
        return

    # Шифруем
    success_count = 0
    error_count = 0
    start_time = datetime.now()

    for i, file in enumerate(py_files, 1):
        print(f"\n[{i}/{len(py_files)}] 🔐 Шифрование {os.path.basename(file)}...")
        try:
            protect(
                input_path=file,
                output_path=file,
                key=config['key'],
                machine=config['machine'],
                expire_days=config['expire_days'] if config['expire_days'] > 0 else None
            )
            print(f"  ✅ {os.path.basename(file)} зашифрован")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            error_count += 1

    # Итоговый отчёт
    elapsed = datetime.now() - start_time
    print("\n" + "=" * 60)
    print("✅ ЗАВЕРШЕНО!")
    print("=" * 60)
    print(f"✅ Успешно зашифровано: {success_count} файлов")
    if error_count > 0:
        print(f"❌ Ошибок: {error_count}")
    print(f"⏱️  Время выполнения: {elapsed.total_seconds():.1f} сек")
    print(f"📁 Результат: {copy_dir}")
    print(f"📂 Оригинал: {target} (не изменён)")

    # Показываем информацию о ключе
    print("\n🔑 Сохраните ключ для расшифровки:")
    print(f"   {config['key']}")
    print("   (без него файлы не запустятся!)")
    print("=" * 60)


if __name__ == "__main__":
    main()