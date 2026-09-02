#!/usr/bin/env python3
import argparse
import base64
import hashlib
import os
import platform
import secrets
import string
import subprocess
import sys
import time
import uuid

MAGIC = b"PythonEncoder|v1|"


def machine_code():
    raw = (
        f"{platform.node()}|"
        f"{uuid.getnode()}|"
        f"{os.environ.get('USER', os.environ.get('USERNAME', ''))}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def derive_key(key: bytes):
    h = hashlib.sha256(MAGIC + key + b"|payload").digest()
    return h * 2


def xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def b64(x: bytes) -> str:
    return base64.b64encode(x).decode("ascii")


def protect(input_path, output_path, key, machine, expire_days):
    with open(input_path, "r", encoding="utf-8-sig") as f:
        source = f.read()

    if key is None:
        key = secrets.token_hex(32)
    key_bytes = key.encode("utf-8")

    if machine is None or machine.lower() == "any":
        machine = "any"
    elif machine.lower() == "auto":
        machine = machine_code()

    machine = machine.replace("|", "_")

    expire_ts = 0
    if expire_days is not None and expire_days > 0:
        expire_ts = int(time.time()) + int(expire_days) * 86400

    dk = derive_key(key_bytes)

    meta = f"{expire_ts}|{machine}"
    meta_enc = xor(meta.encode("utf-8"), dk)
    meta_b64 = b64(meta_enc)

    # Самопроверка
    try:
        decoded = xor(base64.b64decode(meta_b64), dk).decode("utf-8")
        if decoded != meta:
            print(f"Ошибка: метаданные не совпадают. Ожидалось: {meta}, получено: {decoded}")
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка при проверке метаданных: {e}")
        sys.exit(1)

    payload_enc = xor(source.encode("utf-8"), dk)
    payload_b64 = b64(payload_enc)

    key_hex = key_bytes.hex()

    # Обновлённый шаблон с поддержкой импортов
    loader_template = string.Template('''# PythonEncoder generated file. Do not edit manually.
import sys, base64, hashlib, time, os, platform, uuid

_MAGIC = $magic
_KEY_HEX = $key_hex
_EXPIRE = $expire
_META_B64 = $meta_b64
_PAYLOAD_B64 = $payload_b64


def _xor(d, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(d))


def _derive_key(key_hex):
    key = bytes.fromhex(key_hex)
    h = hashlib.sha256(_MAGIC + key + b"|payload").digest()
    return h * 2


def _machine_code():
    raw = (
        f"{platform.node()}|"
        f"{uuid.getnode()}|"
        f"{os.environ.get('USER', os.environ.get('USERNAME', ''))}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _check(machine):
    dk = _derive_key(_KEY_HEX)
    try:
        raw_meta = _xor(base64.b64decode(_META_B64), dk)
        meta = raw_meta.decode("utf-8")
    except UnicodeDecodeError:
        print("PythonEncoder: ошибка: не удалось расшифровать метаданные (возможно, повреждён ключ)")
        print(f"    KEY_HEX = {_KEY_HEX}")
        print(f"    META_B64 = {_META_B64}")
        sys.exit(1)

    exp_str, bound = meta.split("|")
    exp = int(exp_str)

    if bound != machine and bound != "any":
        print("PythonEncoder: ошибка: скрипт защищён для другой машины")
        sys.exit(1)

    if exp and time.time() > exp:
        print("PythonEncoder: ошибка: срок действия истёк")
        sys.exit(1)


def _load():
    """Расшифровывает и выполняет оригинальный код, затем экспортирует все имена."""
    m = _machine_code()
    _check(m)

    dk = _derive_key(_KEY_HEX)
    try:
        raw_code = _xor(base64.b64decode(_PAYLOAD_B64), dk)
        code = raw_code.decode("utf-8")
    except UnicodeDecodeError:
        print("PythonEncoder: ошибка: не удалось расшифровать код (возможно, повреждён ключ)")
        sys.exit(1)

    # Создаём пространство имён с необходимыми переменными
    ns = {}

    # Добавляем стандартные переменные модуля
    ns['__name__'] = __name__
    ns['__file__'] = __file__
    ns['__package__'] = __package__
    ns['__doc__'] = __doc__
    ns['__builtins__'] = __builtins__

    # Добавляем sys и os для поддержки импортов
    ns['sys'] = sys
    ns['os'] = os

    # Копируем глобальные переменные из вызывающего модуля
    # (это важно для корректных относительных импортов)
    try:
        caller_globals = sys._getframe(1).f_globals
        for key in ['__name__', '__package__', '__file__', '__doc__', '__path__']:
            if key in caller_globals:
                ns[key] = caller_globals[key]
    except:
        pass

    try:
        exec(compile(code, "<PythonEncoder>", "exec"), ns)
    except Exception as e:
        print(f"PythonEncoder: ошибка при выполнении кода: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Экспортируем все имена (кроме служебных) в текущий модуль
    for k, v in ns.items():
        if not k.startswith("__") or k in ["__name__", "__file__", "__package__", "__path__"]:
            globals()[k] = v


# Выполняем загрузку при импорте или запуске
_load()
''')

    loader = loader_template.substitute(
        magic=repr(MAGIC),
        key_hex=repr(key_hex),
        expire=expire_ts,
        meta_b64=repr(meta_b64),
        payload_b64=repr(payload_b64)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(loader)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "PythonEncoder: "
            "защита/привязка/срок действия Python-скрипта"
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("machine", help="Показать код машины")

    p_protect = sub.add_parser("protect", help="Защитить .py файл")
    p_protect.add_argument("input", help="Исходный .py файл")
    p_protect.add_argument("-o", "--output", help="Имя выходного файла")
    p_protect.add_argument(
        "--key",
        help="Ключ. Если не указать, будет создан и вшит в файл"
    )
    p_protect.add_argument(
        "--machine",
        help="any, auto или код машины"
    )
    p_protect.add_argument(
        "--no-machine",
        action="store_true",
        help="Не привязывать к машине"
    )
    p_protect.add_argument(
        "--expire-days",
        type=int,
        help="Срок действия в днях"
    )

    p_run = sub.add_parser("run", help="Запустить защищённый файл")
    p_run.add_argument("script")

    args = parser.parse_args()

    if args.command == "machine":
        print(machine_code())

    elif args.command == "protect":
        machine = "any" if args.no_machine else (args.machine or "any")
        out = args.output or args.input
        protect(
            args.input,
            out,
            args.key,
            machine,
            args.expire_days
        )
        print("Готово:", out)

    elif args.command == "run":
        sys.exit(subprocess.call([sys.executable, args.script]))


if __name__ == "__main__":
    main()