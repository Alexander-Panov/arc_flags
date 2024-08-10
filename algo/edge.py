from __future__ import annotations

from dataclasses import dataclass


class Edge:
    u: int  # Откуда
    v: int  # Куда
    weight: float  # Вес ребра

    def __init__(self, u, v, weight, k):
        self.u = u
        self.v = v
        self.weight = weight
        self._flags = [False] * k

    def reversed(self) -> Edge:
        """ Возвращает обратное ребро """
        return Edge(self.v, self.u, self.weight, len(self._flags))

    def set_flag(self, bit):
        self._flags[bit] = True

    def get_flag(self, bit):
        return self._flags[bit]

    def __lt__(self, other: Edge) -> bool:
        """ Два ребра можно сравнивать по весу"""
        return self.weight < other.weight

    def __str__(self) -> str:
        """ Показать вершину красиво в консоли """
        return f"{self.u} -> {self.v}"
