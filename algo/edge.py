from __future__ import annotations


class Edge:
    def __init__(self, u, v, weight, k):
        self.u = u  # Откуда
        self.v = v  # Куда
        self.weight = weight  # Вес ребра
        self._flags = [False] * k  # Флаги ребра для каждого региона

    def reversed(self) -> Edge:
        """ Возвращает обратное ребро """
        return Edge(self.v, self.u, self.weight, len(self._flags))

    def set_flag(self, n):
        """ Поставить n-ый флаг равным True"""
        self._flags[n] = True

    def get_flag(self, bit) -> bool:
        """ Получить значение n-ого флага"""
        return self._flags[bit]

    def __lt__(self, other: Edge) -> bool:
        """ Два ребра можно сравнивать по весу"""
        return self.weight < other.weight

    def __str__(self) -> str:
        """ Показать вершину красиво в консоли """
        return f"{self.u} -> {self.v}"
