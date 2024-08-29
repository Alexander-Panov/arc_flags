from algo.config import DEBUG
from algo.dijkstra.arc_flags import arc_flags_preprocessing
from algo.dijkstra.dijkstra_bidirectional import dijkstra_bidirectional
from algo.dijkstra.dijkstra_unidirectional import dijkstra_unidirectional
from algo.graph import Graph
from algo.vertex import Vertex

if __name__ == '__main__':
    K = 3  # Количество регионов

    # Города
    seattle = Vertex("Seattle", 0)
    san_francisco = Vertex("San Francisco", 0)
    los_angeles = Vertex("Los Angeles", 0)
    riverside = Vertex("Riverside", 0)
    phoenix = Vertex("Phoenix", 0)

    chicago = Vertex("Chicago", 1)
    boston = Vertex("Boston", 1)
    new_york = Vertex("New York", 1)
    detroit = Vertex("Detroit", 1)
    philadelphia = Vertex("Philadelphia", 1)
    washington = Vertex("Washington", 1)

    atlanta = Vertex("Atlanta", 2)
    miami = Vertex("Miami", 2)
    dallas = Vertex("Dallas", 2)
    houston = Vertex("Houston", 2)

    city_graph: Graph = Graph(k=3, vertices=[seattle, san_francisco, los_angeles, riverside, phoenix,
                                             chicago, boston, new_york, detroit, philadelphia, washington,
                                             atlanta, miami, dallas, houston])

    city_graph.add_edge_by_vertices(seattle, chicago, 1737)
    city_graph.add_edge_by_vertices(seattle, san_francisco, 678)
    city_graph.add_edge_by_vertices(san_francisco, riverside, 386)
    city_graph.add_edge_by_vertices(san_francisco, los_angeles, 348)
    city_graph.add_edge_by_vertices(los_angeles, riverside, 50)
    city_graph.add_edge_by_vertices(los_angeles, phoenix, 357)
    city_graph.add_edge_by_vertices(riverside, phoenix, 307)
    city_graph.add_edge_by_vertices(riverside, chicago, 1704)
    city_graph.add_edge_by_vertices(phoenix, dallas, 887)
    city_graph.add_edge_by_vertices(phoenix, houston, 1015)
    city_graph.add_edge_by_vertices(dallas, chicago, 805)
    city_graph.add_edge_by_vertices(dallas, atlanta, 721)
    city_graph.add_edge_by_vertices(dallas, houston, 225)
    city_graph.add_edge_by_vertices(houston, atlanta, 702)
    city_graph.add_edge_by_vertices(houston, miami, 968)
    city_graph.add_edge_by_vertices(atlanta, chicago, 588)
    city_graph.add_edge_by_vertices(atlanta, washington, 543)
    city_graph.add_edge_by_vertices(atlanta, miami, 604)
    city_graph.add_edge_by_vertices(miami, washington, 923)
    city_graph.add_edge_by_vertices(chicago, detroit, 238)
    city_graph.add_edge_by_vertices(detroit, boston, 613)
    city_graph.add_edge_by_vertices(detroit, washington, 396)
    city_graph.add_edge_by_vertices(detroit, new_york, 482)
    city_graph.add_edge_by_vertices(boston, new_york, 190)
    city_graph.add_edge_by_vertices(new_york, philadelphia, 81)
    city_graph.add_edge_by_vertices(philadelphia, washington, 123)
    print(city_graph)

    arc_flags_preprocessing(city_graph)

    if DEBUG:
        print("\n\n*** Визуализация флагов ребер ***")
        print("|  РЕБРО   | 0 | 1 | 2 |")
        for list_edges in city_graph._edges:
            for edge in list_edges:
                flags = edge._flags
                print(f"|{str(edge): ^10}| {flags[0] * 1} | {flags[1] * 1} | {flags[2] * 1 } |")

    print("\n\n*** Однонаправленный поиск (без оптимизации arc_flags): ***")
    distance, path = dijkstra_unidirectional(city_graph, los_angeles, boston, arc_flags=False)
    print("\n*** Однонаправленный поиск (с оптимизацией arc_flags): ***")
    dijkstra_unidirectional(city_graph, los_angeles, boston, arc_flags=True)

    print("\n\n*** Двунаправленный поиск (без оптимизации arc_flags): ***")
    distance, path = dijkstra_bidirectional(city_graph, los_angeles, boston, arc_flags=False)
    print("\n*** Двунаправленный поиск (с оптимизацией arc_flags): ***")
    dijkstra_bidirectional(city_graph, los_angeles, boston, arc_flags=True)


