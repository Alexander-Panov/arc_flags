""" Структуры данных для алгоритма Дейкстры """
from __future__ import annotations

from _heapq import heappush, heappop
from dataclasses import dataclass
from typing import TypeVar, Generic

from algo.edge import Edge

T = TypeVar('T')  # Абстрактный тип - может быть любым типом


class PriorityQueue(Generic[T]):
    """ Класс Очереди с приоритетом"""

    # Generic - может работать с произвольными типом
    # Например: PriorityQueue[int], PriorityQueue[DijkstraNode]
    def __init__(self) -> None:
        self._container: list[T] = []

    @property
    def empty(self) -> bool:
        return not self._container

    def push(self, item: T):
        # Если очередь с приоритетом
        heappush(self._container, item)  # поместить в очередь по приоритету
        # Если простая очередь:
        # self._container.append(item)

    def pop(self) -> T:
        # Если очередь с приоритетом:
        return heappop(self._container)  # извлечь из кучи
        # Если простая очередь
        # return self._container.pop(0)

    def __repr__(self):
        return repr(self._container)


@dataclass
class DijkstraNode:
    """Вспомогательный класс ноды Дейкстры"""
    vertex: int  # индекс вершины
    distance: float  # расстояние от корня до этой вершины

    def __lt__(self, other: DijkstraNode) -> bool:
        """lt - less than - функция сравнения двух DijkstraNode"""
        return self.distance < other.distance

    def __eq__(self, other: DijkstraNode) -> bool:
        """eq - equal - функция сравнения"""
        return self.distance == other.distance


WeightedPath = list[Edge]  # Обозначение WeightedPath (маршрут) как список ребер
