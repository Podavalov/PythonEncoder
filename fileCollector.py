from pathlib import Path

def collect_py_files(directory: str) -> list[str]:
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Указанный путь не является директорией: {directory}")

    py_files = []
    for p in path.rglob('*.py'):
        if not any(part.startswith('.') for part in p.relative_to(path).parts[:-1]):
            py_files.append(str(p))

    return py_files