from algo.dijkstra import PriorityQueue, DijkstraNode, WeightedPath, path_dict_to_path
from algo.edge import Edge
from algo.graph import Graph, V
from algo.utils import clock


@clock
def dijkstra_bidirectional(weighted_graph: Graph, start: V, end: V) -> tuple[float, WeightedPath]:
    """
    Функция двунаправленного поиска кратчайшего маршрута из start в end с применением алгоритма Дейкстры
    :param weighted_graph: взвешенный граф
    :param start: вершина начала поиска
    :param end: вершина конца поиска
    :return: расстояние между вершинами и путь от начала до конца
    """

    def dijkstra_step(queue: PriorityQueue[DijkstraNode],
                      distances: list[float | None],
                      path_dict: dict[int, Edge],
                      visited: set):
        """
        Локальная функция шага алгоритма Дейкстры
        Функция полностью проверяет одну вершину из приоритетной очереди
        :param queue: приоритетная очередь вершин к проверке
        :param distances: уже известные расстояния до вершин к моменту запуска функции
        :param path_dict: уже известный словарь маршрутов к вершинам к моменту запуска функции
        :param visited: множество уже посещенных вершин
        :return: ничего
        """
        if queue.empty:  # если очередь с приоритетом пустая
            return  # функция завершается
        dijkstra_node = queue.pop()
        u = dijkstra_node.vertex
        dist_u = distances[u]
        for we in weighted_graph.edges_of_index(u):
            dist_v = distances[we.v]
            if dist_v is None or dist_v > dist_u + we.weight:
                distances[we.v] = dist_u + we.weight
                path_dict[we.v] = we
                queue.push(DijkstraNode(we.v, distances[we.v]))
        visited.add(u)  # отметить что вершина посещена

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
        dijkstra_step(queue_start, distances_start, path_dict_start, visited_start)
        if visited_start & visited_end:  # {A, Z} & {Z, C} = Z
            # Алгоритм завершит свою работу, когда какая-нибудь вершина z
            # будет удалена из обеих очередей.
            break
        dijkstra_step(queue_end, distances_end, path_dict_end, visited_end)
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
                 path_dict_to_path(end_index, connecting_vertex, path_dict_end)[::-1])  # end -> z (наоборот)

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
                                 path_dict_to_path(end_index, we.v, path_dict_end)[::-1])  # end -> v (наоборот)

    return best_path_length, best_path
