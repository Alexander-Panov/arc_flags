""" Вспомогательные функции """
from __future__ import annotations

from algo.dijkstra.structures import WeightedPath
from algo.edge import Edge
from algo.graph import Graph, V


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
