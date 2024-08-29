from __future__ import annotations

from algo.dijkstra.dijkstra import dijkstra
from algo.dijkstra.utils import path_dict_to_path, print_weighted_path
from algo.graph import Graph
from algo.config import DEBUG


def arc_flags_preprocessing(weighted_graph: Graph):
    """
    Предобработка arc_flags
    :param weighted_graph: Взвешенный граф, где осуществить предобработку
    """
    if DEBUG:
        print("\n*** Начало обработки arc_flags ***")

    for vertex in weighted_graph._vertices:  # для каждой вершины графа
        vertex_index = weighted_graph.index_of(vertex)

        # вызвать обратный алгоритм Дейкстры - дерево кратчайших путей
        distances, path_dict = dijkstra(weighted_graph, vertex, True)

        if DEBUG:
            print(f"\n\tВершина {vertex}")
            print(f"\tВсе вершины дерева кратчайших путей: {list(path_dict.keys())}")

        # Для каждой вершины из дерева кратчайших путей (из которых есть путь в vertex)
        for vertex2_index in path_dict.keys():
            # Получить маршрут до вершины vertex по дереву кратчайших путей
            path = path_dict_to_path(vertex_index, vertex2_index, path_dict, reverse=True)

            if DEBUG:
                print(f"\t\tВетвь до вершины №{vertex2_index}: ", end='')
                print_weighted_path(weighted_graph, path)

            # Установить бит региона vertex для каждого ребра ветви дерева
            for edge in path:
                edge.set_flag(vertex.k)

    if DEBUG:
        print("\n*** Конец обработки arc_flags ***")