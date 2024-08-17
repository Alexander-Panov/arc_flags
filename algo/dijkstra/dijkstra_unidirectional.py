from __future__ import annotations

from algo.dijkstra.dijkstra import dijkstra, dijkstra_step
from algo.dijkstra.structures import WeightedPath, PriorityQueue, DijkstraNode
from algo.dijkstra.utils import path_dict_to_path
from algo.edge import Edge
from algo.graph import Graph
from algo.utils import clock
from algo.vertex import Vertex


@clock
def dijkstra_unidirectional(weighted_graph: Graph, start: Vertex, end: Vertex, arc_flags=False) -> tuple[
    float, WeightedPath]:
    """
    Однонаправленный поиск кратчайшего пути используя алгоритм Дейкстры
    :param weighted_graph: взвешенный граф
    :param start: вершина начала поиска
    :param end: вершина конца поиска
    :param arc_flags: включить оптимизацию arc_flags
    :return: расстояние между вершинами и путь от начала до конца
    """
    start_index = weighted_graph.index_of(start)  # индекс корня
    end_index = weighted_graph.index_of(end)

    distances: list[float | None] = [None] * weighted_graph.vertex_count  # расстояния от корня до каждой вершины
    distances[start_index] = 0  # расстояние от корня до корня

    path_dict: dict[int, Edge] = {}  # Как добраться до каждой вершины
    priority_queue: PriorityQueue[DijkstraNode] = PriorityQueue()
    priority_queue.push(DijkstraNode(start_index, 0))
    while not priority_queue.empty:  # пока очередь с приоритетом не пустая
        dijkstra_step(weighted_graph, priority_queue, distances, path_dict, arc_flags=arc_flags, end=end)

    distance = distances[end_index]  # получить расстояние конкретно до end

    path: WeightedPath = path_dict_to_path(start_index, end_index, path_dict)

    return distance, path
