""" Вспомогательные функции """
from __future__ import annotations

from algo.dijkstra.structures import WeightedPath
from algo.edge import Edge
from algo.graph import Graph
from algo.vertex import Vertex


def path_dict_to_path(start: int, end: int, path_dict: dict[int, Edge], reverse=False) -> WeightedPath:
    """ Получить по path_dict из алгоритма Дейкстры маршрут из вершины start до вершины end"""
    if len(path_dict) == 0:
        return []
    if start == end:
        return []
    edge_path: WeightedPath = []
    e: Edge = path_dict[end]
    edge_path.append(e)
    if not reverse:
        # Все ребра прямые
        while e.u != start:
            e = path_dict[e.u]
            edge_path.append(e)
    else:
        # Все ребра обратные
        while e.v != start:
            e = path_dict[e.v]
            edge_path.insert(0, e)

    return list(reversed(edge_path))



def distance_array_to_vertex_dict(wg: Graph, distances: list[float | None]) -> dict[Vertex, float | None]:
    """Преобразование списка расстояний в словарь расстояний"""
    return {wg.vertex_at(i): distances[i] for i in range(len(distances))}


def print_weighted_path(wg: Graph, path: WeightedPath) -> None:
    """Красиво вывести в консоль маршрут"""
    edge = None
    for edge in path:
        print(f'{wg.vertex_at(edge.u)} -{edge.weight}-> ', end='')
    print(f'{wg.vertex_at(edge.v)}.', end=' ')
    print(f'(Суммарный вес: {total_weight(path)})')


def total_weight(wp: WeightedPath) -> int:
    """Посчитать длину всего маршрута"""
    return sum(edge.weight for edge in wp)
