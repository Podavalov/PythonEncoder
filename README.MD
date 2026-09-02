## PythonEncoder
__**PythonEncoder** — простая учебная программа для базовой защиты Python-скриптов.__

Она умеет:

- защищать `.py` файлы
- запускать защищенные файлы
- показывать код машины
- привязывать скрипт к конкретной машине
- ограничивать срок действия



---
## Возможности

| Функция | Поддержка |
|---|---|
| Защита `.py` файлов | Да |
| Запуск защищенного файла | Да |
| Привязка к машине | Да |
| Срок действия | Да |
| Ключ защиты | Да, упрощенный |


---

## Требования

Нужен Python.

Рекомендуется:

```bash
Python 3.8+
```

Дополнительные библиотеки не нужны.

---



## Основные команды

### 1. `machine`

Показать код текущей машины.

```bash
python guard.py machine
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
python guard.py protect app.py
```



Можно указать имя выходного файла:

```bash
python guard.py protect app.py -o my_app.guarded.py
```

---

### 3. `run`

Запустить защищенный файл.

```bash
python guard.py run app.guarded.py
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
python guard.py protect app.py
```

---

### `-o` / `--output`

Имя выходного файла.

Пример:

```bash
python guard.py protect app.py -o output.py
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
python guard.py protect app.py --key my-secret-key
```

Если защищать несколько файлов с одним и тем же ключом:

```bash
python guard.py protect app1.py --key my-secret-key
python guard.py protect app2.py --key my-secret-key
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
python guard.py protect app.py --machine any
```

Пример привязки к текущей машине:

```bash
python guard.py protect app.py --machine auto
```

Пример привязки к конкретной машине:

```bash
python guard.py protect app.py --machine a1b2c3d4e5f60718
```

---

### `--no-machine`

Простой способ отключить привязку к машине.

Пример:

```bash
python guard.py protect app.py --no-machine
```

Это то же самое:

```bash
python guard.py protect app.py --machine any
```

---

### `--expire-days`

Срок действия в днях.

Пример:

```bash
python guard.py protect app.py --expire-days 30
```

После 30 дней защищенный файл перестанет запускаться.

Пример:

```bash
python guard.py protect app.py --expire-days 7
```

Файл будет работать 7 дней.

Без срока:

```bash
python guard.py protect app.py
```

---

## Примеры использования

### Пример 1. Простая защита

```bash
python guard.py protect app.py
python app.guarded.py
```

---

### Пример 2. Защита с именем выходного файла

```bash
python guard.py protect app.py -o myapp.py
python myapp.py
```

---

### Пример 3. Защита на 30 дней

```bash
python guard.py protect app.py --expire-days 30
python app.guarded.py
```

---

### Пример 4. Защита без привязки к машине

```bash
python guard.py protect app.py --no-machine
python app.guarded.py
```

Такой файл можно запускать на других компьютерах.

---

### Пример 5. Привязка к текущей машине

Сначала посмотрим код машины:

```bash
python guard.py machine
```

Например, получим:

```text
a1b2c3d4e5f60718
```

Защитим файл:

```bash
python guard.py protect app.py --machine a1b2c3d4e5f60718
```

Или проще:

```bash
python guard.py protect app.py --machine auto
```

Такой файл будет работать только на этой машине.

---

### Пример 6. Защита с ключом и сроком

```bash
python guard.py protect app.py --key my-key-123 --expire-days 14
```

---

### Пример 7. Запуск через `run`

```bash
python guard.py run app.guarded.py
```







## Частые ошибки

### Ошибка: срок действия истек

Возможный текст:

```text
PythonEncoder: ошибка: срок действия истек
```

Причина:

файл был создан с параметром `--expire-days`, и срок закончился.

Решение:

создать новый файл защиты.

Пример:

```bash
python guard.py protect app.py --expire-days 30
```

---

### Ошибка: защищен для другой машины

Возможный текст:

```text
PythonEncoder: ошибка: скрипт защищен для другой машины
```

Причина:

файл был привязан к другой машине.

Решение:

либо запустить на правильной машине, либо создать файл без привязки.

Пример:

```bash
python guard.py protect app.py --no-machine
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






## Коротко о том, когда что использовать

| Задача | Команда |
|---|---|
| Просто защитить файл | `python guard.py protect app.py` |
| Запустить защищенный файл | `python guard.py run app.guarded.py` |
| Узнать код машины | `python guard.py machine` |
| Сделать портативную защиту | `python guard.py protect app.py --no-machine` |
| Привязать к машине | `python guard.py protect app.py --machine auto` |
| Ограничить срок | `python guard.py protect app.py --expire-days 30` |

---
