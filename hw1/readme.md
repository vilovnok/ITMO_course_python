# **HW1:** Модель данных и CLI  

## 1.1 Настройка окружения
```py
uv init
uv venv
source .venv/bin/activate
uv sync
```

## 1.2 — Контейнерный тип данных
- Контейнерный тип данных был создан в файле hw_12.py .

## 1.3 — CLI-утилита как installable package
- CLI-утилита была создана в my_wc .

## Основные действия
```
uv sync
source .venv/bin/activate

# запуск контейнерной типы данных
python hw_12.py


# запуск утилиты
uv tool install .
my-wc README.md
```