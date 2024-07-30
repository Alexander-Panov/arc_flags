from heapq import heappush, heappop
from typing import Tuple, List, TypeVar, Generic

from algo.edge import Edge
from algo.graph import Graph, V

T = TypeVar('T')


class PriorityQueue(Generic[T]):
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


def dijkstra(weighted_graph: Graph, root: V) -> tuple[list[float | None], dict[int, Edge]]:
    """
    Алгоритм Дейкстры
    :param weighted_graph: Взвешенный граф, где осуществить поиск
    :param root: Откуда (из какой вершины) осуществить поиск
    :return:
    1. Кратчайшие расстояния до остальных вершин (Числа) (переменная distances)
    2. Кратчайшие пути (маршруты) до остальных вершин (переменная path_dict)
    """
    first: int = weighted_graph.index_of(root)  # индекс корня

    distances: List[float | None] = [None] * weighted_graph.vertex_count  # расстояния от корня до каждой вершины
    distances[first] = 0  # расстояние от корня до корня

    path_dict: dict[int, Edge] = {}
    priority_queue: PriorityQueue[DijkstraNode] = PriorityQueue()
    priority_queue.push(DijkstraNode(first, 0))
    while not priority_queue.empty:
        u: int = priority_queue.pop().vertex
        dist_u: float = distances[u]
        for we in weighted_graph.edges_of_index(u):
            dist_v: float = distances[we.v]
            if dist_v is None or dist_v > dist_u + we.weight:
                distances[we.v] = dist_u + we.weight
                path_dict[we.v] = we
                priority_queue.push(DijkstraNode(we.v, distances[we.v]))
    return distances, path_dict
