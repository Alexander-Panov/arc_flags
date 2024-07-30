from functools import reduce
from operator import add
from typing import TypeVar, Generic, List, Tuple

from edge import Edge

V = TypeVar('V')


class Graph(Generic[V]):
    def __init__(self, vertices: List[V] = []) -> None:
        self._vertices: List[V] = vertices
        self._edges: List[List[Edge]] = [[] for _ in vertices]

    @property
    def vertex_count(self) -> int:
        """ Количество вершин """
        return len(self._vertices)

    @property
    def edges_count(self) -> int:
        """ Количество ребер """
        return len(self._edges)

    def add_vertex(self, vertex: V) -> int:
        """ Добавить новую вершину """
        self._vertices.append(vertex)
        self._edges.append([])
        return self.vertex_count + 1

    def add_edge(self, edge: Edge) -> None:
        """ Добавить новое ребро """
        self._edges[edge.u].append(edge)
        self._edges[edge.v].append(edge.reversed())

    def add_edge_by_indices(self, u: int, v: int, weight: float) -> None:
        """ Добавить ребро между двумя вершинами по индексам """
        self.add_edge(Edge(u, v, weight))

    def add_edge_by_vertices(self, first: V, second: V, weight: float) -> None:
        """ Добавить ребро между двумя вершинами """
        u: int = self._vertices.index(first)
        v: int = self._vertices.index(second)
        self.add_edge_by_indices(u, v, weight)

    def vertex_at(self, i: int) -> V:
        """ Вернуть вершину под индексом """
        return self._vertices[i]

    def index_of(self, vertex: V) -> int:
        """ Найти индекс вершины """
        return self._vertices.index(vertex)

    def neighbors_of_index(self, index: int) -> List[V]:
        """ Получить соседей вершины по индексу """
        return list(map(self.vertex_at, [edge.v for edge in self._edges[index]]))

    def neighbour_of_vertex(self, vertex: V) -> List[V]:
        """ Получить соседей вершины """
        return self.neighbors_of_index(self.index_of(vertex))

    def neighbors_for_index_with_weights(self, index: int) -> List[Tuple[V, float]]:
        return [(self.vertex_at(edge.v), edge.weight) for edge in self.edges_of_index(index)]

    def edges_of_index(self, index: int) -> List[Edge]:
        """ Получить ребра вершины по индексу """
        return self._edges[index]

    def edges_of_vertex(self, vertex: V) -> List[V]:
        """ Получить ребра вершины """
        return self.edges_of_index(self.index_of(vertex))

    def __str__(self) -> str:
        """ Показать красиво в консоли """
        return reduce(add, [f"{self._vertices[i]} -> {self.neighbors_for_index_with_weights(i)}\n" for i in
                            range(self.vertex_count)],
                      "")
