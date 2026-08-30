from pathlib import Path


def collect_py_files(directory: str) -> list[str]:
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Указанный путь не является директорией: {directory}")
    return [str(p) for p in path.rglob('*.py')]

def encode_file(file_path):
    pass


# Пример использования
if __name__ == "__main__":
    target = input("Введите путь к директории: ")
    try:
        py_files = collect_py_files(target)
        print(f"Найдено файлов .py: {len(py_files)}")
        for file in py_files:
            encode_file(file)
    except ValueError as e:
        print(f"Ошибка: {e}")
