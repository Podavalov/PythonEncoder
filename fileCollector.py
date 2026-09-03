from pathlib import Path

# Список файлов и шаблонов, которые НЕ будут шифроваться
EXCLUDED_PATTERNS = [
    'setup.py',
    'settings.py',
    '__init__.py',
    'conftest.py',
    '*_test.py',
    'test_*.py',
    '*_encrypted*',
    '*.guarded.py',
    '*.enc.py',
    'manage.py',
    'wsgi.py',
    'asgi.py',
    'settings.py',
    'urls.py',
    'views.py',
    '*/migrations/*.py',
    '*/migrations/__init__.py',
    'conftest.py',
    'settings.py',
    'local_settings.py',
    'dev_settings.py',
    'prod_settings.py',
    'setup.py',
    'celery.py',
    'tasks.py',
    'celery_app.py',
    'admin.py',
    'apps.py',
    'models.py',
    'forms.py',
    'serializers.py',
    'permissions.py',
    'celery.py',
    'celery_app.py',
    'tasks.py',

]


def is_excluded(filename: str, patterns: list = None) -> bool:
    """Проверяет, должен ли файл быть исключён из обработки."""
    if patterns is None:
        patterns = EXCLUDED_PATTERNS

    file_path = Path(filename)
    file_name = file_path.name

    for pattern in patterns:
        # Если шаблон содержит звёздочку, используем glob-сопоставление
        if '*' in pattern:
            # Используем Path.match для glob-шаблонов
            if file_path.match(pattern) or file_name.startswith(pattern.replace('*', '')):
                return True
        # Точное совпадение
        elif file_name == pattern:
            return True
        # Проверка, не содержит ли путь исключаемую директорию
        elif pattern in str(file_path):
            return True

    return False


def collect_py_files(directory: str, exclude_patterns: list = None) -> list[str]:

    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Указанный путь не является директорией: {directory}")

    if exclude_patterns is None:
        exclude_patterns = EXCLUDED_PATTERNS

    py_files = []
    for p in path.rglob('*.py'):
        # Пропускаем файлы в скрытых папках (начинаются с .)
        if any(part.startswith('.') for part in p.relative_to(path).parts[:-1]):
            continue

        # Проверяем, не исключён ли файл
        if not is_excluded(str(p), exclude_patterns):
            py_files.append(str(p))

    return py_files


def get_exclusion_list() -> list:
    """Возвращает текущий список исключений."""
    return EXCLUDED_PATTERNS.copy()


def add_exclusion(pattern: str):
    """Добавляет новый шаблон в список исключений."""
    if pattern not in EXCLUDED_PATTERNS:
        EXCLUDED_PATTERNS.append(pattern)


def remove_exclusion(pattern: str):
    """Удаляет шаблон из списка исключений."""
    if pattern in EXCLUDED_PATTERNS:
        EXCLUDED_PATTERNS.remove(pattern)