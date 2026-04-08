import time
from functools import wraps
from typing import Callable, Any



def validate_types(dummy: bool = True) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Проверяет аргументы и возвращаемое значение по аннотациям.
    dummy - это просто опциональный параметр, который не влияет на поведение.
    """
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            annot = fn.__annotations__

            keys = [k for k in annot if k != "return"]
            for i, value in enumerate(args):
                if i >= len(keys):
                    break
                expected = annot[keys[i]]
                if expected and not isinstance(value, expected):
                    raise TypeError(f"{keys[i]} должен быть {expected}, получено {type(value)}")

            for key, value in kwargs.items():
                expected = annot.get(key)
                if expected and not isinstance(value, expected):
                    raise TypeError(f"{key} должен быть {expected}, получено {type(value)}")

            result = fn(*args, **kwargs)
            expected_return = annot.get("return")
            if expected_return and not isinstance(result, expected_return):
                raise TypeError(f"возврат должен быть {expected_return}, получено {type(result)}")

            return result
        return wrapper
    return decorator


def memoize(ttl=None) ->  Callable[..., Any]:
    """Кэширование с ttl в секундах"""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        cache = {}

        @wraps(fn)
        def wrapper(*args: tuple, **kwargs: dict) -> object:
            key = (args, tuple(kwargs.items()))
            now = time.time()

            if key in cache:
                value, timestamp = cache[key]
                if ttl is None or now - timestamp < ttl:
                    return value

            result = fn(*args, **kwargs)
            cache[key] = (result, now)

            return result
        return wrapper
    return decorator


def retry(times: int, delay: float, exceptions: tuple) -> Callable[..., Any]:
    """Повтор с экспоненциальным backoff."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: tuple, **kwargs: dict) -> object:
            current_delay = delay
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    time.sleep(current_delay)
                    current_delay *= 2

        return wrapper
    return decorator