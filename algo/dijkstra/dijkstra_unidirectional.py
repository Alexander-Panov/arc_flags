from __future__ import annotations

from algo.dijkstra.dijkstra import dijkstra
from algo.dijkstra.structures import WeightedPath
from algo.dijkstra.utils import path_dict_to_path
from algo.graph import Graph, V
from algo.utils import clock


@clock
def dijkstra_unidirectional(weighted_graph: Graph, start: V, end: V) -> tuple[float, WeightedPath]:
    """
    Однонаправленный поиск кратчайшего пути используя алгоритм Дейкстры
    :param weighted_graph: взвешенный граф
    :param start: вершина начала поиска
    :param end: вершина конца поиска
    :return: расстояние между вершинами и путь от начала до конца
    """
    start_index = weighted_graph.index_of(start)
    end_index = weighted_graph.index_of(end)

    distances, path_dict = dijkstra(weighted_graph, start)  # получает дерево кратчайших путей из start
    distance = distances[end_index]  # получить расстояние до end

    path: WeightedPath = path_dict_to_path(start_index, end_index, path_dict)

    return distance, path
