from __future__ import annotations

from dataclasses import dataclass


@dataclass  # dataclass автоматически создает инициализатор __init__() и прочее
class Edge:
    u: int  # Откуда
    v: int  # Куда
    weight: float  # Вес ребра

    def reversed(self) -> Edge:
        """ Возвращает обратное ребро """
        return Edge(self.v, self.u, self.weight)

    def __lt__(self, other: Edge) -> bool:
        """ Два ребра можно сравнивать по весу"""
        return self.weight < other.weight

    def __str__(self) -> str:
        """ Показать вершину красиво в консоли """
        return f"{self.u} -> {self.v}"
