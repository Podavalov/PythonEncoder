Ниже — простой и понятный `README` для программы из прошлого ответа. Можно сохранить как файл `README.md`.

---

# Mini Guard

**Mini Guard** — простая учебная программа для базовой защиты Python-скриптов.

Она умеет:

- защищать `.py` файлы
- запускать защищенные файлы
- показывать код машины
- привязывать скрипт к конкретной машине
- ограничивать срок действия
- работать как мини-аналог базовой защиты Python-кода

> Важно: это учебная и простая реализация, а не полноценный промышленный аналог PyArmor.

---

## Возможности

| Функция | Поддержка |
|---|---|
| Защита `.py` файлов | Да |
| Запуск защищенного файла | Да |
| Привязка к машине | Да |
| Срок действия | Да |
| Ключ защиты | Да, упрощенный |
| Полная VM-защита | Нет |
| Продакшен-лицензирование | Нет |
| Антиотладка | Нет |

---

## Требования

Нужен Python.

Рекомендуется:

```bash
Python 3.8+
```

Дополнительные библиотеки не нужны.

---

## Быстрый старт

Создадим простой скрипт:

```bash
echo 'print("Привет, мир!")' > app.py
```

Защитим его:

```bash
python mini_guard.py protect app.py
```

Появится новый файл:

```bash
app.guarded.py
```

Запустим:

```bash
python app.guarded.py
```

Ожидаемый результат:

```text
Привет, мир!
```

---

## Основные команды

### 1. `machine`

Показать код текущей машины.

```bash
python mini_guard.py machine
```

Пример вывода:

```text
a1b2c3d4e5f60718
```

Этот код можно использовать для привязки защищенного файла к конкретной машине.

---

### 2. `protect`

Защитить Python-файл.

Пример:

```bash
python mini_guard.py protect app.py
```

Без параметров команда создаст файл:

```bash
app.guarded.py
```

Можно указать имя выходного файла:

```bash
python mini_guard.py protect app.py -o my_app.guarded.py
```

---

### 3. `run`

Запустить защищенный файл.

```bash
python mini_guard.py run app.guarded.py
```

Эквивалент:

```bash
python app.guarded.py
```

---

## Параметры команды `protect`

### `input`

Исходный Python-файл.

Пример:

```bash
python mini_guard.py protect app.py
```

---

### `-o` / `--output`

Имя выходного файла.

Пример:

```bash
python mini_guard.py protect app.py -o output.py
```

Если параметр не указан, будет создан файл:

```bash
app.guarded.py
```

---

### `--key`

Ключ защиты.

Если ключ не указать, программа создаст случайный и вставит его в защищенный файл.

Пример:

```bash
python mini_guard.py protect app.py --key my-secret-key
```

Если защищать несколько файлов с одним и тем же ключом:

```bash
python mini_guard.py protect app1.py --key my-secret-key
python mini_guard.py protect app2.py --key my-secret-key
```

---

### `--machine`

Привязка к машине.

Возможные значения:

| Значение | Что делает |
|---|---|
| `any` | Не привязывать к машине |
| `auto` | Привязать к текущей машине |
| код машины | Привязать к конкретной машине |

Пример без привязки:

```bash
python mini_guard.py protect app.py --machine any
```

Пример привязки к текущей машине:

```bash
python mini_guard.py protect app.py --machine auto
```

Пример привязки к конкретной машине:

```bash
python mini_guard.py protect app.py --machine a1b2c3d4e5f60718
```

---

### `--no-machine`

Простой способ отключить привязку к машине.

Пример:

```bash
python mini_guard.py protect app.py --no-machine
```

Это то же самое:

```bash
python mini_guard.py protect app.py --machine any
```

---

### `--expire-days`

Срок действия в днях.

Пример:

```bash
python mini_guard.py protect app.py --expire-days 30
```

После 30 дней защищенный файл перестанет запускаться.

Пример:

```bash
python mini_guard.py protect app.py --expire-days 7
```

Файл будет работать 7 дней.

Без срока:

```bash
python mini_guard.py protect app.py
```

---

## Примеры использования

### Пример 1. Простая защита

```bash
python mini_guard.py protect app.py
python app.guarded.py
```

---

### Пример 2. Защита с именем выходного файла

```bash
python mini_guard.py protect app.py -o myapp.py
python myapp.py
```

---

### Пример 3. Защита на 30 дней

```bash
python mini_guard.py protect app.py --expire-days 30
python app.guarded.py
```

---

### Пример 4. Защита без привязки к машине

```bash
python mini_guard.py protect app.py --no-machine
python app.guarded.py
```

Такой файл можно запускать на других компьютерах.

---

### Пример 5. Привязка к текущей машине

Сначала посмотрим код машины:

```bash
python mini_guard.py machine
```

Например, получим:

```text
a1b2c3d4e5f60718
```

Защитим файл:

```bash
python mini_guard.py protect app.py --machine a1b2c3d4e5f60718
```

Или проще:

```bash
python mini_guard.py protect app.py --machine auto
```

Такой файл будет работать только на этой машине.

---

### Пример 6. Защита с ключом и сроком

```bash
python mini_guard.py protect app.py --key my-key-123 --expire-days 14
```

---

### Пример 7. Запуск через `run`

```bash
python mini_guard.py run app.guarded.py
```

---

## Как это работает?

Очень упрощенно:

1. Программа читает исходный `.py` файл.
2. Создает ключ.
3. Шифрует исходник.
4. Генерирует новый файл-обертку.
5. При запуске новый файл:
   - проверяет срок действия,
   - проверяет привязку к машине,
   - расшифровывает исходник,
   - запускает его.

---

## Что получится после защиты?

Было:

```bash
app.py
```

Стало:

```bash
app.guarded.py
```

Или, если указали `-o`:

```bash
myapp.py
```

Оригинальный `app.py` при этом не изменяется.

---

## Важно знать

### Это не полная защита

Mini Guard подходит для учебных целей и простых задач.

Она не защищает полностью от:

- вытаскивания ключа
- декомпиляции
- модификации сгенерированного файла
- отладки
- запуску кода в памяти
- реверс-инжиниринга

Для защиты коммерческого продукта лучше использовать более серьезные решения.

---

## Частые ошибки

### Ошибка: срок действия истек

Возможный текст:

```text
mini-guard: ошибка: срок действия истек
```

Причина:

файл был создан с параметром `--expire-days`, и срок закончился.

Решение:

создать новый файл защиты.

Пример:

```bash
python mini_guard.py protect app.py --expire-days 30
```

---

### Ошибка: защищен для другой машины

Возможный текст:

```text
mini-guard: ошибка: скрипт защищен для другой машины
```

Причина:

файл был привязан к другой машине.

Решение:

либо запустить на правильной машине, либо создать файл без привязки.

Пример:

```bash
python mini_guard.py protect app.py --no-machine
```

---

### Файл не запускается

Проверьте:

```bash
python app.guarded.py
```

Убедитесь, что:

- Python установлен,
- файл существует,
- путь указан правильно.

Пример:

```bash
cd /path/to/folder
python app.guarded.py
```

---

## Пример полного цикла

```bash
# 1. Создаем обычный скрипт
echo 'print("Hello Mini Guard")' > hello.py

# 2. Смотрим код машины
python mini_guard.py machine

# 3. Защищаем файл
python mini_guard.py protect hello.py -o hello.guarded.py --expire-days 30

# 4. Запускаем
python hello.guarded.py
```

Результат:

```text
Hello Mini Guard
```

---

## Команды коротко

```bash
# Код машины
python mini_guard.py machine

# Защита
python mini_guard.py protect app.py

# Защита в конкретный файл
python mini_guard.py protect app.py -o app.guarded.py

# Защита с ключом
python mini_guard.py protect app.py --key secret

# Защита на 30 дней
python mini_guard.py protect app.py --expire-days 30

# Защита без привязки к машине
python mini_guard.py protect app.py --no-machine

# Привязка к текущей машине
python mini_guard.py protect app.py --machine auto

# Запуск
python mini_guard.py run app.guarded.py
```

---

## Коротко о том, когда что использовать

| Задача | Команда |
|---|---|
| Просто защитить файл | `python mini_guard.py protect app.py` |
| Запустить защищенный файл | `python mini_guard.py run app.guarded.py` |
| Узнать код машины | `python mini_guard.py machine` |
| Сделать портативную защиту | `python mini_guard.py protect app.py --no-machine` |
| Привязать к машине | `python mini_guard.py protect app.py --machine auto` |
| Ограничить срок | `python mini_guard.py protect app.py --expire-days 30` |

---

## Ограничения

Mini Guard **не является**:

- полноценной VM-защитой,
- системой лицензирования,
- продакшен-инструментом,
- заменой PyArmor/Nuitka/ComPyler,
- защитой от квалифицированного взлома.

Она подходит, если нужно:

- защитить учебный скрипт,
- сделать простую заготовку,
- понять, как работает базовая защита Python-кода,
- создать собственный инструмент дальше.

---

## Лицензия

Для учебных целей.

Перед использованием в коммерческом проекте проверьте юридическую сторону и назначение инструмента.