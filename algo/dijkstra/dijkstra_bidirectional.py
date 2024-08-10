from algo.dijkstra.dijkstra import dijkstra_step
from algo.dijkstra.structures import WeightedPath, PriorityQueue, DijkstraNode
from algo.dijkstra.utils import path_dict_to_path
from algo.edge import Edge
from algo.graph import Graph
from algo.utils import clock
from algo.vertex import Vertex


@clock
def dijkstra_bidirectional(weighted_graph: Graph, start: Vertex, end: Vertex, arc_flags=False) -> tuple[float, WeightedPath]:
    """
    Функция двунаправленного поиска кратчайшего маршрута из start в end с применением алгоритма Дейкстры
    :param weighted_graph: взвешенный граф
    :param start: вершина начала поиска
    :param end: вершина конца поиска
    :param arc_flags: включить оптимизацию arc_flags
    :return: расстояние между вершинами и путь от начала до конца
    """

    # Для start и end получаем их индексы
    start_index = weighted_graph.index_of(start)
    end_index = weighted_graph.index_of(end)

    # Для start и end заводим собственные списки расстояний
    distances_start: list[float | None] = [None] * weighted_graph.vertex_count
    distances_end: list[float | None] = [None] * weighted_graph.vertex_count
    distances_start[start_index] = 0
    distances_end[end_index] = 0

    # Для start и end заводим собственные словари маршрутов
    path_dict_start: dict[int, Edge] = {}
    path_dict_end: dict[int, Edge] = {}

    # Для start и end заводим собственные очереди посещения вершин
    queue_start = PriorityQueue[DijkstraNode]()
    queue_end = PriorityQueue[DijkstraNode]()
    queue_start.push(DijkstraNode(start_index, 0))
    queue_end.push(DijkstraNode(end_index, 0))

    # Для start и end заводим собственные множества посещенных вершин
    visited_start = set()
    visited_end = set()

    while not queue_start.empty and not queue_end.empty:
        dijkstra_step(weighted_graph, queue_start, distances_start, path_dict_start, visited=visited_start,
                      arc_flags=arc_flags)
        if visited_start & visited_end:  # {A, Z} & {Z, C} = Z
            # Алгоритм завершит свою работу, когда какая-нибудь вершина z
            # будет удалена из обеих очередей.
            break
        dijkstra_step(weighted_graph, queue_end, distances_end, path_dict_end, visited=visited_end, reverse=True,
                      arc_flags=arc_flags)
        if visited_start & visited_end:  # {A, Z} & {Z, C} = Z
            break

    if not visited_start & visited_end:
        # Если нет ни одной вершины и там и там
        return float('inf'), []  # Расстояние между вершинами считать бесконечными, а пути не существует

    connecting_vertex = (visited_start & visited_end).pop()  # Получить вершину, которая была посещена в двух очередях

    # Лучшее (кратчайшее) расстояние
    best_path_length = distances_start[connecting_vertex] + distances_end[connecting_vertex]
    # На данный момент лучший путь содержит общую посещенную вершину
    # Лучший маршрут
    best_path = (path_dict_to_path(start_index, connecting_vertex, path_dict_start) +  # start -> z
                 path_dict_to_path(end_index, connecting_vertex, path_dict_end, reverse=True))  # z -> end

    # Скорость работы O(M + N), где M - количество вершин, N - количество ребер
    for u in range(weighted_graph.vertex_count):  # по каждой вершине в графе
        for we in weighted_graph.edges_of_index(u):  # для каждого ее ребра (которое состоит из u и v)
            # Есть ли до этой вершины пути из start и end
            if distances_start[u] is not None and distances_end[we.v] is not None:
                path_length = distances_start[u] + we.weight + distances_end[we.v]
                if path_length < best_path_length:
                    best_path_length = path_length
                    best_path = (path_dict_to_path(start_index, u, path_dict_start) +  # start -> u
                                 [we] +  # u -> v
                                 path_dict_to_path(end_index, we.v, path_dict_end, reverse=True))  # v -> end

    return best_path_length, best_path
