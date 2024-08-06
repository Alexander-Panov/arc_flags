from __future__ import annotations

from dataclasses import dataclass
from heapq import heappush, heappop
from typing import TypeVar, Generic

from algo.utils import clock
from edge import Edge
from graph import Graph, V

""" Структуры данных для алгоритма Дейкстры """

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


""" Алгоритм Дейкстры """


def dijkstra_all(weighted_graph: Graph, root: V) -> tuple[list[float | None], dict[int, Edge]]:
    """
    Алгоритм Дейкстры от корня до всех вершин в графе
    Получает дерево кратчайших путей до корня
    :param weighted_graph: Взвешенный граф, где осуществить поиск
    :param root: Откуда (из какой вершины) осуществить поиск
    :return:
    1. Кратчайшие расстояния до остальных вершин (Числа) (переменная distances)
    2. Кратчайшие пути (маршруты) до остальных вершин (переменная path_dict)
    """
    first: int = weighted_graph.index_of(root)  # индекс корня

    distances: list[float | None] = [None] * weighted_graph.vertex_count  # расстояния от корня до каждой вершины
    distances[first] = 0  # расстояние от корня до корня

    path_dict: dict[int, Edge] = {}  # Как добраться до каждой вершины
    priority_queue: PriorityQueue[DijkstraNode] = PriorityQueue()
    priority_queue.push(DijkstraNode(first, 0))
    while not priority_queue.empty:  # пока очередь с приоритетом не пустая
        dijkstra_node = priority_queue.pop()
        u: int = dijkstra_node.vertex  # Исследуем ближайшую вершину
        # u - текущая вершина, с которой начинается поиск
        dist_u: float = distances[u]  # Рассмотреть все ребра и вершины для данной вершины
        # dist_u - сохраненное расстояние, по которому можно добратвься до u по известным маршрутам

        # Рассмотреть все ребра и вершины для данной вершины
        for we in weighted_graph.edges_of_index(u):  # Вот тут уже не очень понятно
            # Старое расстояние до этой вершины
            dist_v: float = distances[we.v]

            # Затем исследуются ребра связанные с u и dist_v
            # Это расстояние до всех известных вершины, соединенных ребром с u

            # Старого расстояние не существует или найден более короткий путь
            if dist_v is None or dist_v > dist_u + we.weight:
                # Меняем расстояние до этой вершины
                distances[we.v] = dist_u + we.weight
                # Заменить ребро на более короткий путь к этой вершине
                path_dict[we.v] = we
                # Перемещаем все вершины с новыми путями в очередь с приоритетом
                priority_queue.push(DijkstraNode(we.v, distances[we.v]))

    # Возвращаем расстояние от корневой вершины до каждой и path_dict, что позволяет определить
    # Кратчайшие пути к ним
    return distances, path_dict


@clock
def dijkstra(weighted_graph: Graph, start: V, end: V) -> tuple[float, WeightedPath]:
    """
    Поиск кратчайшего пути через однонаправленный поиск алгоритма Дейкстры
    :param weighted_graph: взвешенный граф
    :param start: вершина начала поиска
    :param end: вершина конца поиска
    :return: расстояние между вершинами и путь от начала до конца
    """
    start_index = weighted_graph.index_of(start)
    end_index = weighted_graph.index_of(end)

    distances, path_dict = dijkstra_all(weighted_graph, start)  # получает дерево кратчайших путей из start
    distance = distances[end_index]  # получить расстояние до end

    path: WeightedPath = path_dict_to_path(start_index, end_index, path_dict)

    return distance, path


""" Вспомогательные функции """

WeightedPath = list[Edge]  # Обозначение WeightedPath (маршрут) как список ребер


def path_dict_to_path(start: int, end: int, path_dict: dict[int, Edge]) -> WeightedPath:
    """ Получить по path_dict из алгоритма Дейкстры маршрут из вершины start до вершины end"""
    if len(path_dict) == 0:
        return []
    edge_path: WeightedPath = []
    e: Edge = path_dict[end]
    edge_path.append(e)
    while e.u != start:
        e = path_dict[e.u]
        edge_path.append(e)
    return list(reversed(edge_path))


def distance_array_to_vertex_dict(wg: Graph[V], distances: list[float | None]) -> dict[V, float | None]:
    """Преобразование списка расстояний в словарь расстояний"""
    return {wg.vertex_at(i): distances[i] for i in range(len(distances))}


def print_weighted_path(wg: Graph, path: WeightedPath) -> None:
    """Красиво вывести в консоль маршрут"""
    for edge in path:
        print(f'{wg.vertex_at(edge.u)} -{edge.weight}-> {wg.vertex_at(edge.v)}')
    print(f'Суммарный вес: {total_weight(path)}')


def total_weight(wp: WeightedPath) -> int:
    """Посчитать длину всего маршрута"""
    return sum(edge.weight for edge in wp)
