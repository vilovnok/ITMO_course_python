import json

from typing import Any, Callable, Dict, List, TypeVar, cast


Row = TypeVar("Row", bound=Dict[str, Any])
T = TypeVar("T")
R = TypeVar("R")


def filter_by(**rules: str) -> Callable[[List[Row]], List[Row]]:
    """Фильтрация списка словарей по заданным правилам"""
    
    def fn(data: List[Row]) -> List[Row]:
        def check(item: Row) -> bool:
            for key, rule in rules.items():
                value = item.get(key)
                if value is None:
                    return False

                if rule.startswith(">"):
                    if not value > float(rule[1:]):
                        return False
                elif rule.startswith("<"):
                    if not value < float(rule[1:]):
                        return False
                elif rule.startswith("=="):
                    if str(value) != rule[2:]:
                        return False
                else:
                    if str(value) != rule:
                        return False

            return True
        return [item for item in data if check(item)]
    return fn


def sort_by(key: str) -> Callable[[List[Row]], List[Row]]:
    """Возвращает функцию сортировки списка словарей по ключу"""
    def fn(data: List[Row]) -> List[Row]:
        result = data.copy()
        result.sort(key=lambda x: x.get(key, ""))
        
        return result
    return fn


def take(n: int) -> Callable[[List[T]], List[T]]:
    """Возвращает функцию, которая берёт первые n элементов"""
    def fn(data: List[T]) -> List[T]:
        return data[:n]
    return fn


def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Создаёт пайплайн функций слева направо"""
    if not funcs:
        raise ValueError("Требуется по крайней мере одна функция")

    def fn(arg: Any) -> Any:
        result: Any = arg
        for f in funcs:
            result = f(result)
        
        return result
    return fn


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Создаёт композицию функций справа налево"""
    if not funcs:
        raise ValueError("Требуется по крайней мере одна функция")

    def fn(arg: Any) -> Any:
        result: Any = arg
        for f in reversed(funcs):
            result = f(result)
        
        return result
    return fn




if __name__ == "__main__":
    def read_csv(path: str):
        return [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 30},
            {"name": "David", "age": 20},
        ]

    def to_json(data: List[Dict[str, Any]]) -> str:
        return json.dumps(data, ensure_ascii=False)

    pipeline = pipe(
        read_csv,
        filter_by(age=">18"),
        sort_by("name"),
        take(2),
        to_json
    )

    print(pipeline("data.csv"))