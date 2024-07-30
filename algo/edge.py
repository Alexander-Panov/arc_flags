from __future__ import annotations

from dataclasses import dataclass


@dataclass  # dataclass автоматически создает инициализатор __init__() и прочее
class Edge:
    u: int  # from
    v: int  # to
    weight: float  # Вес

    def reversed(self) -> Edge:
        """ Возвращает обратное ребро """
        return Edge(self.v, self.u, self.weight)

    def __lt__(self, other: Edge) -> bool:
        """ Две вершины можно сравнивать по весу"""
        return self.weight < other.weight

    def __str__(self) -> str:
        """ Показать вершину красиво в консоли """
        return f"{self.u} -> {self.v}"

