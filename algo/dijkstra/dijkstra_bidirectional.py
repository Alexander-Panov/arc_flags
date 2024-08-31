from algo.config import DEBUG
from algo.dijkstra.dijkstra import dijkstra_step
from algo.dijkstra.structures import WeightedPath, PriorityQueue, DijkstraNode
from algo.dijkstra.utils import path_dict_to_path, print_weighted_path
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
    if DEBUG:
        print("\t* Начало двунаправленного поиска")

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

    if DEBUG:
        print(f"\n\tИНИЦИАЛИЗАЦИЯ")
        print(f"\t{start_index=}")
        print(f"\t{end_index=}")
        print(f"\tРасстояния до каждой вершины от start: {distances_start}")
        print(f"\tРасстояния до каждой вершины от end: {distances_end}")
        print(f"\tОчередь с приоритетом для start: {queue_start}")
        print(f"\tОчередь с приоритетом для end: {queue_end}")
        print(f"\tСловарь путей start: {path_dict_start}")
        print(f"\tСловарь путей end: {path_dict_end}")
        print(f"\tПосещенные вершины из start: {visited_start}")
        print(f"\tПосещенные вершины из end: {visited_end}")
        step = 0

    while not queue_start.empty and not queue_end.empty:
        if DEBUG:
            step += 1
            print(f"\n\tШАГ №{step} - START:")
        dijkstra_step(weighted_graph, queue_start, distances_start, path_dict_start, visited=visited_start,
                      arc_flags=arc_flags, end=end)
        if DEBUG:
            print(f"\tРасстояния до каждой вершины от start: {distances_start}")
            print(f"\tОчередь с приоритетом для start: {queue_start}")
            print(f"\tСловарь путей start: {path_dict_start}")
            print(f"\tПосещенные вершины из start: {visited_start}")

        if visited_start & visited_end:  # {A, Z} & {Z, C} = Z
            # Алгоритм завершит свою работу, когда какая-нибудь вершина z
            # будет удалена из обеих очередей.
            break

        if DEBUG:
            print(f"\n\tШАГ №{step} - END:")
        dijkstra_step(weighted_graph, queue_end, distances_end, path_dict_end, visited=visited_end, reverse=True,
                      arc_flags=arc_flags, end=end)
        if DEBUG:
            print(f"\tРасстояния до каждой вершины от end: {distances_end}")
            print(f"\tОчередь с приоритетом для end: {queue_end}")
            print(f"\tСловарь путей end: {path_dict_end}")
            print(f"\tПосещенные вершины из end: {visited_end}")

        if visited_start & visited_end:  # {A, Z} & {Z, C} = Z
            break

    if not visited_start & visited_end:
        if DEBUG:
            print("\n\t* Результат: ")
            print("\t\t Пути не существует")
        # Если нет ни одной вершины и там и там
        return float('inf'), []  # Расстояние между вершинами считать бесконечными, а пути не существует

    connecting_vertex = (visited_start & visited_end).pop()  # Получить вершину, которая была посещена в двух очередях

    if DEBUG:
        print(f"\n\tКонцы встретились в вершине {connecting_vertex}")
    # Лучшее (кратчайшее) расстояние
    best_path_length = distances_start[connecting_vertex] + distances_end[connecting_vertex]
    # На данный момент лучший путь содержит общую посещенную вершину
    # Лучший маршрут
    best_path = (path_dict_to_path(start_index, connecting_vertex, path_dict_start) +  # start -> z
                 path_dict_to_path(end_index, connecting_vertex, path_dict_end, reverse=True))  # z -> end

    if DEBUG:
        print(f"\n\t ПОИСК ЛУЧШЕГО ПУТИ:")
        print(f"\t Лучшее (кратчайшее) расстояние: {best_path_length}")
        print(f"\t Лучший путь: {best_path}")
        print(f"\n\t ПЕРЕБОР ВСЕХ ВЕРШИН ГРАФА:")


    # ! Кратчайший путь не обязательно пройдёт через вершину connecting_vertex
    # Перебираем каждую посещенную из start вершину (кроме connecting_vertex) + start_index
    for u in (visited_start - {connecting_vertex} | {start_index}):
        if DEBUG:
            print(f"\t\tВЕРШИНА {u}:")
        for we in weighted_graph.edges_of_index(u):  # для каждого исходящего ребра этой вершины (которое состоит из u и v)
            # Есть ли до конца этого ребра существует путь из end
            if distances_end[we.v] is not None:
                if DEBUG:
                    print(f"\t\t\tРЕБРО {we}:")
                if arc_flags:  # Включена оптимизация arc flags
                    if not we.get_flag(end.k):  # Если это ребро не лежит на кратчайшем пути в регион вершины end
                        print(f"\t\t\t(оптимизация arc flags) ребро пропущено, так не содержится в кратчайшим пути до региона '{end.k}'")
                        continue  # пропустить его
                path_length = distances_start[u] + we.weight + distances_end[we.v]  # считаем продолжительность нового пути через вершину u
                if path_length < best_path_length:  # Если новый путь короче предыдущего наилучшего пути
                    if DEBUG:
                        print(f"\t\t\t! Найдена более короткий путь")
                        print(f"\t\t\tСтарая длина пути: {best_path_length}")
                        print(f"\t\t\tНовая длина пути: {path_length}")
                        print(f"\t\t\tСтарый путь: {best_path}")
                    best_path_length = path_length
                    best_path = (path_dict_to_path(start_index, u, path_dict_start) +  # start -> u
                                 [we] +  # u -> v
                                 path_dict_to_path(end_index, we.v, path_dict_end, reverse=True))  # v -> end
                    if DEBUG:
                        print(f"\t\t\tНовый путь: {best_path}")
                else:
                    if DEBUG:
                        print(f"\t\t\t Ребро не дает путь короче, отбрасываем")

    if DEBUG:
        print("\n\t* Результат: ")
        print("\t\t Кратчайший путь из Los Angeles в Boston:")
        print('\t\t ', end='')
        print_weighted_path(weighted_graph, best_path)
        print("\t* Конец двунаправленного поиска")

    return best_path_length, best_path
