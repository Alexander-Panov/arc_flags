""" Алгоритм Дейкстры """
from __future__ import annotations

from algo.config import DEBUG
from algo.dijkstra.structures import PriorityQueue, DijkstraNode
from algo.edge import Edge
from algo.graph import Graph
from algo.vertex import Vertex


def dijkstra_step(weighted_graph: Graph,
                  priority_queue: PriorityQueue[DijkstraNode],
                  distances: list[float | None],
                  path_dict: dict[int, Edge], *,
                  reverse: bool = False,
                  arc_flags: bool = False,
                  visited: set = None,
                  end: Vertex = None):
    """
    Функция шага алгоритма Дейкстры.
    Функция полностью проверяет одну вершину из приоритетной очереди
    :param weighted_graph: взвешенный граф
    :param priority_queue: приоритетная очередь вершин к проверке
    :param distances: уже известные расстояния до вершин к моменту запуска функции
    :param path_dict: уже известный словарь маршрутов к вершинам к моменту запуска функции
    :param reverse: рассматривать "выходящие" из вершины ребра или "входящие" (по умолчанию "выходящие")
    :param arc_flags: включить оптимизацию arc_flags
    :param visited: множество уже посещенных вершин (None если не нужно отмечать посещенные вершины (для dijkstra, unidirectional_dijkstra)
    :param end: конечная вершина, к который мы ищем путь
    :return: ничего
    """
    if priority_queue.empty:  # если очередь с приоритетом пустая
        return  # функция завершается
    dijkstra_node = priority_queue.pop()
    u: int = dijkstra_node.vertex  # Исследуем ближайшую вершину
    # u - текущая вершина, с которой начинается поиск
    dist_u: float = distances[u]  # Рассмотреть все ребра и вершины для данной вершины
    # dist_u - сохраненное расстояние, по которому можно добраться до u по известным маршрутам

    # Рассмотреть все ребра и вершины для данной вершины (выходящие или входящие в зависимости от reversed)

    if not reverse:
        edges = weighted_graph.edges_of_index(u)  # получить выходящие из вершины ребра
    else:
        edges = weighted_graph.reversed_edges_of_index(u)  # получить входящие в вершину ребра

    if DEBUG:
        print(f"\tИсследуем вершину: {u}")
        print(f"\tИсследуемые ребра: {edges}")

    for we in edges:  # цикл по полученным ребрам текущей вершины
        if DEBUG:
            print(f"\t\tРЕБРО {we}:")
        if not reverse:
            vertex = we.v
        else:
            vertex = we.u
        dist_v: float = distances[vertex]  # известное расстояние до вершины v
        # Затем исследуются ребра связанные с u и dist_v
        # Это расстояние до всех известных вершины, соединенных ребром с u

        # Если включена оптимизация arc_flags
        if arc_flags:
            # Если это ребро не находится на пути в нужный регион вершины
            if not we.get_flag(end.k):
                if DEBUG:
                    print(f"\t\t(оптимизация arc flags) ребро пропущено, так не содержится в кратчайшим пути до региона '{end.k}'")
                continue   # ребро не рассматриваем

        # Условие Дейкстры: старого расстояния не существует или найден более короткий путь
        if dist_v is None or dist_v > dist_u + we.weight:
            # Меняем расстояние до этой вершины
            distances[vertex] = dist_u + we.weight
            # Заменить ребро на более короткий путь к этой вершине
            path_dict[vertex] = we
            # Перемещаем все вершины с новыми путями в очередь с приоритетом
            priority_queue.push(DijkstraNode(vertex, distances[vertex]))

            if DEBUG:
                print(f"\t\t! Найдена более короткий путь до вершины {vertex}")
                print(f"\t\tСтарое расстояние: {dist_v}")
                print(f"\t\tНовое расстояние: {dist_u + we.weight}")
                print(f"\t\tВершина {vertex} добавлена в очередь с приоритетом")
        else:
            # Если не выполняется условие - ребро не рассматриваем
            if DEBUG:
                print(f"\t\t Ребро не дает путь короче, отбрасываем")
            pass
    if visited is not None:
        visited.add(u)  # отметить что вершина посещена


def dijkstra(weighted_graph: Graph, root: Vertex, reverse=False) -> tuple[
    list[float | None], dict[int, Edge]]:
    """
    Алгоритм Дейкстры от конкретной вершины до всех вершин в графе.
    Получает дерево кратчайших путей от конкретной вершины
    :param weighted_graph: Взвешенный граф, где осуществить поиск
    :param root: Откуда (из какой вершины) осуществить поиск
    :param reverse: включить обратный алгоритм Дейкстры (ищутся кратчайшие пути из всех вершин в root)
    :param arc_flags: включить оптимизацию arc_flags
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
        dijkstra_step(weighted_graph, priority_queue, distances, path_dict, reverse=reverse)

    # Возвращаем расстояние от корневой вершины до каждой и path_dict, что позволяет определить
    # Кратчайшие пути к ним
    return distances, path_dict
