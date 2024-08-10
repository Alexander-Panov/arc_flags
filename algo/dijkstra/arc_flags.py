from __future__ import annotations

from algo.dijkstra.dijkstra import dijkstra
from algo.dijkstra.structures import PriorityQueue, DijkstraNode
from algo.edge import Edge
from algo.graph import Graph


def arc_flags_preprocessing(weighted_graph: Graph):
    """
    Предобработка arc_flags
    :param weighted_graph: Взвешенный граф, где осуществить предобработку
    """
    for vertex in weighted_graph._vertices:
        dijkstra(weighted_graph, vertex, True)
