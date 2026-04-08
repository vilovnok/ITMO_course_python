# richard-decorators

Лёгкая библиотека с переиспользуемыми декораторами для Python: проверка типов, кэширование и retry-логика.

## Установка из TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/richard-decorators
```

## Что внутри

- `validate_types` — проверка аргументов и результата по аннотациям
- `memoize` — кэширование результата с опциональным TTL
- `retry` — повтор вызова с экспоненциальной backoff

## Пример использования

### memoize
```python
from richard_decorators import memoize
import time

@memoize()
def slow_square(x: int) -> int:
    time.sleep(1)
    return x * x

print(slow_square(4))  
print(slow_square(4))  

# Output: 1 sec
# Output: мгновенно
```

### validate_types
```python
from richard_decorators import validate_types

@validate_types(enabled=True)
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2))

# Output: 3
```

### retry
```python
from richard_decorators import retry

attempt = 0

@retry(times=3, delay=0.5, exceptions=(ValueError,))
def unstable_function():
    global attempt
    attempt += 1
    print(f"Попытка {attempt}")
    
    if attempt < 3:
        raise ValueError("Ошибка")
    
    return "Успех"

print(unstable_function())

# Output:
# Попытка 1
# Попытка 2
# Попытка 3
# Успех
```