from __future__ import annotations

from algo.config import DEBUG
from algo.dijkstra.dijkstra import dijkstra, dijkstra_step
from algo.dijkstra.structures import WeightedPath, PriorityQueue, DijkstraNode
from algo.dijkstra.utils import path_dict_to_path, print_weighted_path
from algo.edge import Edge
from algo.graph import Graph
from algo.utils import clock
from algo.vertex import Vertex


@clock
def dijkstra_unidirectional(weighted_graph: Graph, start: Vertex, end: Vertex, arc_flags=False) -> tuple[
    float, WeightedPath, int]:
    """
    Однонаправленный поиск кратчайшего пути используя алгоритм Дейкстры
    :param weighted_graph: взвешенный граф
    :param start: вершина начала поиска
    :param end: вершина конца поиска
    :param arc_flags: включить оптимизацию arc_flags
    :return: расстояние между вершинами, путь от начала до конца, количество операций
    """
    count_op = 0  # Счетчик кол-ва операций

    if DEBUG:
        print("\t* Начало однонаправленного поиска")

    start_index = weighted_graph.index_of(start)  # индекс корня
    end_index = weighted_graph.index_of(end)

    distances: list[float | None] = [None] * weighted_graph.vertex_count  # расстояния от корня до каждой вершины
    distances[start_index] = 0  # расстояние от корня до корня

    path_dict: dict[int, Edge] = {}  # Как добраться до каждой вершины
    priority_queue: PriorityQueue[DijkstraNode] = PriorityQueue()
    priority_queue.push(DijkstraNode(start_index, 0))

    if DEBUG:
        print(f"\n\tИНИЦИАЛИЗАЦИЯ")
        print(f"\t{start_index=}")
        print(f"\t{end_index=}")
        print(f"\tРасстояния до каждой вершины: {distances}")
        print(f"\tОчередь с приоритетом: {priority_queue}")
        print(f"\tСловарь путей: {path_dict}")
        step = 0
    while not priority_queue.empty:  # пока очередь с приоритетом не пустая
        if DEBUG:
            step += 1
            print(f"\n\tШАГ №{step}")
        # Вызвать шаг алгоритма Дейкстры и прибавить количество выполненных операций
        count_op += dijkstra_step(weighted_graph, priority_queue, distances, path_dict, arc_flags=arc_flags, end=end)
        if DEBUG:
            print(f"\tРасстояния до каждой вершины: {distances}")
            print(f"\tОчередь с приоритетом: {priority_queue}")
            print(f"\tСловарь путей: {path_dict}")

    distance = distances[end_index]  # получить расстояние конкретно до end

    if DEBUG:
        print("\n\t* Результат: ")

    if distance is None:
        if DEBUG:
            print("\t\t Пути не существует")
        distance, path = float('inf'), []
    else:
        path: WeightedPath = path_dict_to_path(start_index, end_index, path_dict)
        if DEBUG:
            print("\t\t Кратчайший путь из Los Angeles в Boston:")
            print('\t\t ', end='')
            print_weighted_path(weighted_graph, path)

    if DEBUG:
        print("\t* Конец однонаправленного поиска")
    return distance, path, count_op
