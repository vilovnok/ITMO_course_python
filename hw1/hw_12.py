from collections.abc import Iterable, MutableSequence, Iterator


class RingBuffer(MutableSequence):
    """Циклический буфер фиксированного размера"""

    def __init__(self, max_length: int, items: Iterable | None = None) -> None:
        if max_length <= 0:
            raise ValueError("max_length должен быть больше 0")

        self.max_length: int = max_length
        self._items: list = []

        if items is not None:
            for item in items:
                self.append(item)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> object:
        return self._items[index]

    def __setitem__(self, index: int, value: object) -> None:
        self._items[index] = value

    def __delitem__(self, index: int) -> None:
        del self._items[index]

    def insert(self, index: int, value: object) -> None:
        if len(self._items) == self.max_length:
            self._items.pop(0)
            if index > 0:
                index -= 1
        self._items.insert(index, value)

    def append(self, value: object) -> None:
        if len(self._items) == self.max_length:
            self._items.pop(0)
        self._items.append(value)

    def __iter__(self) -> Iterator:
        return iter(self._items)

    def __reversed__(self) -> Iterator:
        return reversed(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __repr__(self) -> str:
        return f"RingBuffer(max_length={self.max_length}, items={self._items})"

    def __str__(self) -> str:
        return str(self._items)



if __name__ == "__main__":
    c = RingBuffer(max_length=5, items=[1, 2, 3])
    print("Изначальный буфер:", c)

    print("Длина буфера:", len(c))

    c.append(4)
    c.append(5)
    print("После добавления 4 и 5:", c)

    c.append(6)
    print("После добавления 6 (переполнение):", c)

    print("Элемент с индексом 2:", c[2])
    c[1] = 22

    print("После изменения элемента с индексом 1:", c)

    del c[0]
    print("После удаления элемента с индексом 0:", c)

    print("Итерируем буфер:")
    for x in c:
        print(x, end=" ")
    print()

    print("Буфер в обратном порядке:")
    for x in reversed(c):
        print(x, end=" ")
    print()

    print("Есть ли 99 в буфере?", 22 in c)

    print("repr буфера:", repr(c))