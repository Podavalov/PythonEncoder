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

MAGIC = b"mini-guard|v1|"


def machine_code():
    raw = (
        f"{platform.node()}|"
        f"{uuid.getnode()}|"
        f"{os.environ.get('USER', os.environ.get('USERNAME', ''))}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def derive_key(key):
    h = hashlib.sha256(MAGIC + key + b"|payload").digest()
    return h * 2


def xor(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def b64(x):
    return base64.b64encode(x).decode("ascii")


def protect(input_path, output_path, key, machine, expire_days):
    with open(input_path, "r", encoding="utf-8-sig") as f:
        source = f.read()

    if not key:
        key = secrets.token_hex(32)

    key_bytes = key.encode("utf-8")

    if machine is None or machine.lower() == "any":
        machine = "any"
    elif machine.lower() == "auto":
        machine = machine_code()

    machine = machine.replace("|", "_")

    if expire_days is not None and expire_days > 0:
        expire_ts = int(time.time()) + int(expire_days) * 86400
    else:
        expire_ts = 0

    dk = derive_key(key_bytes)

    payload = b64(xor(source.encode("utf-8"), dk))

    meta = f"{expire_ts}|{machine}"
    meta_payload = b64(xor(meta.encode("utf-8"), dk))

    key_chunks = [
        bytes(key_bytes[i:i + 8])
        for i in range(0, max(1, len(key_bytes)), 8)
    ]
    key_literal = "[" + ", ".join(repr(x) for x in key_chunks) + "]"

    chunk = 60
    lines = [
        f'    "{payload[i:i + chunk]}"'
        for i in range(0, len(payload), chunk)
    ]
    if not lines:
        lines = ['    ""']

    payload_expr = "(\n" + "\n".join(lines) + "\n)"

    loader_template = string.Template(
        """# mini-guard generated file. Do not edit manually.
import sys, base64, hashlib, time, os, platform, uuid

_MAGIC = $magic
_KEY_PARTS = $key_literal
_EXPIRE = $expire_ts
_META_B64 = $meta_payload
_PAYLOAD_B64 = $payload_expr


def _xor(d, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(d))


def _derive_key(parts):
    h = hashlib.sha256(_MAGIC + b"".join(parts) + b"|payload").digest()
    return h * 2


def _machine_code():
    raw = (
        f"{platform.node()}|"
        f"{uuid.getnode()}|"
        f"{os.environ.get('USER', os.environ.get('USERNAME', ''))}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _check(machine):
    dk = _derive_key(_KEY_PARTS)
    meta = base64.b64decode(
        _xor(base64.b64decode(_META_B64), dk)
    ).decode("utf-8")

    exp, bound = meta.split("|")

    if bound != machine and bound != "any":
        print("mini-guard: ошибка: скрипт защищен для другой машины")
        sys.exit(1)

    if int(exp) and time.time() > int(exp):
        print("mini-guard: ошибка: срок действия истек")
        sys.exit(1)


def _run():
    m = _machine_code()
    _check(m)

    dk = _derive_key(_KEY_PARTS)
    code = base64.b64decode(
        _xor(base64.b64decode(_PAYLOAD_B64), dk)
    ).decode("utf-8")

    ns = {
        "__name__": "__main__",
        "__file__": __file__,
        "__doc__": None,
        "__package__": None,
        "__loader__": None,
        "__spec__": None,
    }

    exec(compile(code, "<mini-guard>", "exec"), ns)


_run()
"""
    )

    loader = loader_template.substitute(
        magic=repr(MAGIC),
        key_literal=key_literal,
        expire_ts=expire_ts,
        meta_payload=repr(meta_payload),
        payload_expr=payload_expr,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(loader)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Учебный мини-аналог PyArmor: "
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

    p_run = sub.add_parser("run", help="Запустить защищенный файл")
    p_run.add_argument("script")

    args = parser.parse_args()

    if args.command == "machine":
        print(machine_code())

    elif args.command == "protect":
        machine = "any" if args.no_machine else (args.machine or "any")
        out = args.output or args.input + ".guarded.py"
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
