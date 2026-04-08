from typing import List
import logging



class Validated:
    def __init__(self, type=None, min=None, max=None):
        self.type = type
        self.min = min
        self.max = max

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if self.type and not isinstance(value, self.type):
            raise TypeError(f"{self.name[1:]} должно быть {self.type}")
        if self.min is not None and value < self.min:
            raise ValueError(f"{self.name[1:]} должно быть >= {self.min}")
        if self.max is not None and value > self.max:
            raise ValueError(f"{self.name[1:]} должно быть <= {self.max}")
        setattr(obj, self.name, value)


class Logged:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        val = getattr(obj, self.name)
        logging.info(f"[LOG] get {self.name[1:]} = {val}")
        return val

    def __set__(self, obj, value):
        logging.info(f"[LOG] set {self.name[1:]} = {value}")
        setattr(obj, self.name, value)


class Cached:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            value = obj.method(self.name[1:])  
            setattr(obj, self.name, value)
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        setattr(obj, self.name, value)


class MatrixFileMixin:
    @classmethod
    def from_file(cls, path: str):
        with open(path, "r") as f:
            data = [[float(x) for x in line.split()] for line in f]
        return cls(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Matrix(MatrixFileMixin):
    rows = Validated(type=int, min=1)
    cols = Validated(type=int, min=1)
    data = Logged()
    determinant = Cached()

    def __init__(self, data: List[List[float]]):
        
        self.data = tuple(
            tuple(float(x) for x in row) 
            for row in data
        )
        
        if not self.data or any(len(row) != len(self.data[0]) for row in self.data):
            raise ValueError("Матрица пустая или строки разной длины")
        
        self.shape = (len(self.data), len(self.data[0]))
        self.rows = len(data)
        self.cols = len(data[0])

    def __add__(self, other: "Matrix") -> "Matrix":
        self._check_shape(other)
        return Matrix([[a + b for a, b in zip(r1, r2)] for r1, r2 in zip(self.data, other.data)])

    def __sub__(self, other: "Matrix") -> "Matrix":
        self._check_shape(other)
        return Matrix([[a - b for a, b in zip(r1, r2)] for r1, r2 in zip(self.data, other.data)])

    def __mul__(self, scalar: float) -> "Matrix":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Matrix([[a * scalar for a in row] for row in self.data])

    def __matmul__(self, other: "Matrix") -> "Matrix":
        if self.shape[1] != other.shape[0]:
            raise ValueError("Размерности не согласованы для умножения")
        return Matrix([[sum(self.data[i][k] * other.data[k][j] for k in range(self.shape[1]))
                        for j in range(other.shape[1])] for i in range(self.shape[0])])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Matrix) and self.data == other.data

    def __hash__(self) -> int:
        return hash(self.data)

    def __repr__(self) -> str:
        return f"Matrix({[list(row) for row in self.data]})"

    def __str__(self) -> str:
        return "\n".join("\t".join(f"{x:g}" for x in row) for row in self.data)

    def __format__(self, fmt: str) -> str:
        return "\n".join("\t".join(format(x, fmt) for x in row) for row in self.data)

    def _check_shape(self, other: "Matrix"):
        if self.shape != other.shape:
            raise ValueError("Матрицы должны иметь одинаковый размер")

    def method(self, attr):
        if attr == "determinant":
            if self.shape[0] != self.shape[1]:
                raise ValueError("Детерминант можно вычислить только для квадратной матрицы")
            
            import numpy as np
            return float(np.linalg.det(np.array(self.data)))




if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    m1 = Matrix([[1, 2], [3, 4]])
    m2 = Matrix([[5, 6], [7, 8]])
    m3 = Matrix([[1, 2], [3, 4]]) 

    matrix_set = {m1, m2}
    matrix_dict = {m1: "first", m2: "second"}

    print("Set:", matrix_set)
    print("Dict:", matrix_dict)

    class BadMatrix(Matrix):
        def __hash__(self):
            return 42 

    bm1 = BadMatrix([[1, 2]])
    bm2 = BadMatrix([[3, 4]])

    print("\nHashes (коллизия):", hash(bm1), hash(bm2))
    print("bm1 == bm2?", bm1 == bm2)

    bad_set = {bm1, bm2} 
    print("Set с коллизией:", bad_set)

    # Объяснение
    # Если нарушить этот инвариант (a == b, но hash(a) != hash(b)), 
    # то словари и множества будут работать некорректно: одинаковые объекты
    # могут оказаться "разными" в dict/set. Python может хранить их как разные ключи.