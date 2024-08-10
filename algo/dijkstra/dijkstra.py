""" Алгоритм Дейкстры """
from __future__ import annotations

from algo.dijkstra.structures import PriorityQueue, DijkstraNode
from algo.edge import Edge
from algo.graph import Graph, V


def dijkstra_step(weighted_graph: Graph,
                  priority_queue: PriorityQueue[DijkstraNode],
                  distances: list[float | None],
                  path_dict: dict[int, Edge],
                  visited: set = None):
    """
    Функция шага алгоритма Дейкстры.
    Функция полностью проверяет одну вершину из приоритетной очереди
    :param weighted_graph: взвешенный граф
    :param priority_queue: приоритетная очередь вершин к проверке
    :param distances: уже известные расстояния до вершин к моменту запуска функции
    :param path_dict: уже известный словарь маршрутов к вершинам к моменту запуска функции
    :param visited: множество уже посещенных вершин
    :return: ничего
    """
    if priority_queue.empty:  # если очередь с приоритетом пустая
        return  # функция завершается
    dijkstra_node = priority_queue.pop()
    u: int = dijkstra_node.vertex  # Исследуем ближайшую вершину
    # u - текущая вершина, с которой начинается поиск
    dist_u: float = distances[u]  # Рассмотреть все ребра и вершины для данной вершины
    # dist_u - сохраненное расстояние, по которому можно добратвься до u по известным маршрутам

    # Рассмотреть все ребра и вершины для данной вершины
    for we in weighted_graph.edges_of_index(u):
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
    if visited is not None:
        visited.add(u)  # отметить что вершина посещена


def dijkstra(weighted_graph: Graph, root: V) -> tuple[list[float | None], dict[int, Edge]]:
    """
    Алгоритм Дейкстры от корня до всех вершин в графе.
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
        dijkstra_step(weighted_graph, priority_queue, distances, path_dict)

    # Возвращаем расстояние от корневой вершины до каждой и path_dict, что позволяет определить
    # Кратчайшие пути к ним
    return distances, path_dict
