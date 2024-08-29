from dataclasses import dataclass


@dataclass(frozen=True)  # неизменяемый
class Vertex:
    id: str  # id вершины (в нашем случае - Название города)
    k: int  # регион

    def __str__(self) -> str:
        """ Показать имя в консоли """
        return f"{self.id} (регион {self.k})"

    def __repr__(self) -> str:
        return self.id