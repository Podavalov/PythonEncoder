from pathlib import Path

def collect_py_files(directory: str) -> list[str]:
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Указанный путь не является директорией: {directory}")
    return [str(p) for p in path.rglob('*.py')]