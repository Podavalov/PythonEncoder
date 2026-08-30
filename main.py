from fileCollector import collect_py_files as coll
from fileEncoder import encode_file as encode

if __name__ == "__main__":
    target = input("Введите путь к директории: ")
    try:
        py_files = coll(target)
        print(f"Найдено файлов .py: {len(py_files)}")
        for file in py_files:
            encode(file)
    except ValueError as e:
        print(f"Ошибка: {e}") 
