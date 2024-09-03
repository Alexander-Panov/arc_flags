from __future__ import annotations

import json
import sys
import time

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap, QColor, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMenu, QMessageBox
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent

from algo.config import DEBUG
from algo.dijkstra.arc_flags import arc_flags_preprocessing
from algo.dijkstra.dijkstra_bidirectional import dijkstra_bidirectional
from algo.dijkstra.dijkstra_unidirectional import dijkstra_unidirectional
from algo.dijkstra.structures import WeightedPath
from algo.graph import Graph
from algo.vertex import Vertex
from gui.color_squares import ColorSquaresDialog
from gui.config import DARK_GREEN, COLORS, K


class CustomViewBox(pg.ViewBox):
    def __init__(self, graph, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.addItem(self.graph)


class GraphGUI(pg.GraphItem):
    def __init__(self, main_window: MainWindow, **kwargs):
        self.data = {}
        self.main_window = main_window
        self.textItems = []
        self.texts = []
        self.points_colors = []
        self.arrows = []
        self.edges = []  # Список графических элементов рёбер

        self.graph: Graph | None = None

        super().__init__(**kwargs)

        self.dragging_edge = False  # Флаг, показывающий, что идёт добавление ребра
        self.start_vertex = None  # Начальная вершина для ребра
        self.temp_arrow = None  # Временная стрелка, которую пользователь тянет
        self.temp_line = None

        self.find_method = None  # Сохранение выбранного режима поиска
        self.arc_flags = False
        # Добавление переменных для начальной и конечной вершин
        self.start_vertex = None
        self.end_vertex = None

        self.scatter.sigClicked.connect(self.scatter_right_click)

    def setData(self, **kwargs):
        self.data = kwargs
        if 'texts' in self.data:
            self.texts = self.data.pop('texts', [])
            self.setTexts(self.texts)
        if 'points_colors' in self.data:
            self.points_colors = self.data.pop('points_colors')
            self.data['symbolBrush'] = [pg.mkBrush(color=color) for color in self.points_colors]
            self.data['symbolPen'] = [pg.mkPen(width=0) for _ in self.points_colors]
        if 'adj' in self.data:
            self.data['edgePen'] = [pg.mkPen(width=5) for _ in self.data['adj']]
            self.data['arrowBrush'] = [pg.mkBrush(color='w') for _ in self.data['adj']]
        self.data['pen'] = pg.mkPen(width=5)
        self.updateGraph()

    def setTexts(self, text):
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        for t in text:
            item = pg.TextItem(t)
            self.textItems.append(item)
            item.setParentItem(self)

    def updateGraph(self):
        super().setData(**self.data)
        for i, item in enumerate(self.textItems):
            item.setPos(*self.pos[i])
        self.scatter.setAcceptHoverEvents(True)
        self.drawArrows()
        self.fillGraph()

    def fillGraph(self):
        vertices = []
        for text, color in zip(self.texts, self.points_colors):
            # noinspection PyTypeChecker
            vertices.append(Vertex(text, list(COLORS.values()).index(tuple(color))))

        self.graph = Graph(k=K, vertices=vertices)

        if self.adjacency is not None:
            for (v1, v2), edge in zip(self.adjacency, self.edges):
                x_data, y_data = edge.getData()

                # Вычисляем разности между соседними точками
                dx = np.diff(x_data)
                dy = np.diff(y_data)

                # Вычисляем длины отрезков между точками
                segment_lengths = np.sqrt(dx ** 2 + dy ** 2)
                self.graph.add_edge_by_indices(int(v1), int(v2), float(segment_lengths[0]))

        arc_flags_preprocessing(self.graph)

        if DEBUG:
            print(self.graph)

    def mouseDragEvent(self, ev):
        ev.accept()
        pos = ev.pos()

        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first
            # pressed:
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = int(self.dragPoint.index())
            self.dragOffset = self.pos[ind] - pos
        if ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = int(self.dragPoint.index())
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        self.updateGraph()
        ev.accept()

    def hoverEvent(self, ev):
        if self.dragging_edge and self.temp_arrow:
            # Обновление временной стрелки, которая следует за курсором
            self.update_temp_line_arrow(ev.pos())

    def mouseClickEvent(self, event: MouseClickEvent):
        """ Сброс всех режимов """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging_edge:
                self.finish_adding_edge(None)
            if self.find_method:
                self.reset_find()
        elif event.button() == Qt.MouseButton.RightButton:
            context_menu = QMenu()

            # Add vertex action
            add_vertex_action = QAction('Добавить вершину', self)
            add_vertex_action.triggered.connect(lambda: self.add_vertex(event.pos()))
            context_menu.addAction(add_vertex_action)

            context_menu.exec(event.screenPos().toPoint())

    def reset_find(self):
        self.main_window.statusBar().clearMessage()
        self.data['symbolPen'] = [pg.mkPen(width=0) for _ in self.points_colors]
        self.data['edgePen'] = [pg.mkPen(width=5) for _ in self.data['adj']]
        self.data['arrowBrush'] = [pg.mkBrush(color='w') for _ in self.data['adj']]

        self.find_method = None
        self.start_vertex = None
        self.end_vertex = None

        self.updateGraph()

    def drawArrows(self, color='w'):
        for arrow in self.arrows:
            arrow.scene().removeItem(arrow)
        self.arrows = []

        # Удаляем предыдущие графические элементы рёбер
        for edge in self.edges:
            self.getViewBox().removeItem(edge)
        self.edges = []

        if self.adjacency is not None:
            for edge, pen in zip(self.adjacency, self.data['edgePen']):
                start = self.pos[edge[0]]
                end = self.pos[edge[1]]

                # Создание графического элемента для ребра
                line = pg.PlotCurveItem([start[0], end[0]], [start[1], end[1]], pen=pen, clickable=True)
                # Добавление события нажатия на ребро
                line.sigClicked.connect(self.edge_click)

                self.getViewBox().addItem(line)
                self.edges.append(line)
        if self.adjacency is not None:
            for edge, brush in zip(self.adjacency, self.data['arrowBrush']):
                start = self.pos[edge[0]]
                end = self.pos[edge[1]]
                arrow = pg.ArrowItem(pos=end,
                                     angle=np.degrees(np.arctan2((end[1] - start[1]), end[0] - start[0])) + 180,
                                     brush=brush,
                                     headLen=0.7,
                                     pxMode=False)
                self.arrows.append(arrow)
                self.getViewBox().addItem(arrow)

    def scatter_right_click(self, scatter, points, event):
        if points:
            if self.find_method:
                if self.start_vertex is None:
                    self.start_vertex = points[0]
                    self.data['symbolPen'][int(self.start_vertex.index())] = pg.mkPen(width=5, color=DARK_GREEN)
                    self.updateGraph()

                    self.main_window.statusBar().showMessage(
                        "2. Выберите конечную вершину (или нажмите на поле чтобы отменить)")
                elif self.end_vertex is None:
                    self.end_vertex = points[0]
                    self.data['symbolPen'][int(self.end_vertex.index())] = pg.mkPen(width=5, color=DARK_GREEN)
                    self.updateGraph()

                    self.main_window.statusBar().showMessage("Запуск алгоритма")
                    self.main_window.run_algorithm()
            elif self.dragging_edge:
                self.finish_adding_edge(points[0])
            elif not self.dragging_edge:
                context_menu = QMenu()
                # Действие "Удалить вершину"
                delete_action = QAction("Удалить вершину", context_menu)
                delete_action.triggered.connect(lambda: self.remove_vertex(points[0]))
                context_menu.addAction(delete_action)

                # Действие "Перекрасить вершину"
                color_menu = QMenu("Перекрасить вершину", context_menu)
                context_menu.addMenu(color_menu)

                # Добавление опций цветов в подменю
                for color_name, rgb in COLORS.items():
                    color_action = QAction(color_name.capitalize(), color_menu)
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(QColor(*rgb))
                    color_action.setIcon(QIcon(pixmap))
                    color_action.triggered.connect(lambda _, c=rgb: self.recolor_vertex(points[0], c))
                    color_menu.addAction(color_action)

                # Действие "Добавить ребро"
                add_edge_action = QAction("Добавить ребро", context_menu)
                add_edge_action.triggered.connect(lambda: self.start_adding_edge(points[0]))
                context_menu.addAction(add_edge_action)

                context_menu.exec(event.screenPos().toPoint())

    def update_temp_line_arrow(self, end_pos):
        # Обновляем временную стрелку, которая следует за курсором
        start_pos = self.start_vertex.pos()
        angle = np.degrees(np.arctan2((end_pos.y() - start_pos.y()), end_pos.x() - start_pos.x())) + 180
        self.temp_arrow.setPos(end_pos)
        self.temp_arrow.setStyle(angle=angle)

        self.temp_line.setData([start_pos.x(), end_pos.x()], [start_pos.y(), end_pos.y()])

    def start_adding_edge(self, start_vertex):
        self.dragging_edge = True
        self.start_vertex = start_vertex

        self.temp_arrow = pg.ArrowItem(angle=0, brush=pg.mkBrush('w'), headLen=0.7, pxMode=False)
        self.getViewBox().addItem(self.temp_arrow)
        self.temp_line = pg.PlotCurveItem(pen=pg.mkPen(width=5))
        self.getViewBox().addItem(self.temp_line)

        self.update_temp_line_arrow(self.start_vertex.pos())

    def finish_adding_edge(self, end_vertex):
        if end_vertex is not None and end_vertex != self.start_vertex:
            self.add_edge(self.start_vertex, end_vertex)

        # Убираем временную стрелку и сбрасываем флаг добавления ребра
        self.getViewBox().removeItem(self.temp_arrow)
        self.getViewBox().removeItem(self.temp_line)

        self.dragging_edge = False
        self.start_vertex = None
        self.temp_arrow = None

    def edge_click(self, line, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Контекстное меню для удаления ребра
            context_menu = QMenu()
            delete_action = QAction("Удалить ребро", context_menu)
            delete_action.triggered.connect(lambda: self.remove_edge(line))
            context_menu.addAction(delete_action)

            show_flags_action = QAction("Посмотреть флаги", context_menu)
            show_flags_action.triggered.connect(lambda: self.show_flags(line))
            context_menu.addAction(show_flags_action)
            context_menu.exec(event.screenPos().toPoint())

    def remove_edge(self, line):
        # Удаление графического элемента ребра
        self.getViewBox().removeItem(line)

        # Удаление ребра из списка рёбер
        if line in self.edges:
            index = self.edges.index(line)
            self.edges.pop(index)
            # Также удаляем ребро из списка смежности
            self.adjacency = np.delete(self.adjacency, index, axis=0)
            # Обновляем граф без удалённого ребра
            self.setData(**(self.data | {'adj': self.adjacency}))

    def add_edge(self, start_vertex, end_vertex):
        start_index = int(start_vertex.index())
        end_index = int(end_vertex.index())

        # Проверка, что такое ребро еще не существует
        if not any((edge == [start_index, end_index]).all() for edge in self.adjacency):
            self.adjacency = np.vstack([self.adjacency, [start_index, end_index]])
            self.setData(**(self.data | {'adj': self.adjacency}))

    def add_vertex(self, pos):
        new_pos = np.array([pos.x(), pos.y()])

        # Add new position to the existing ones
        self.pos = np.vstack([self.pos, new_pos])

        # Optionally, add a default text and color for the new vertex
        self.texts.append(f"Point {int(self.texts[-1].split()[1]) + 1}")
        self.points_colors.append((255, 255, 255))  # Default color (white)

        # Update the graph with the new vertex
        self.setData(**(self.data | {"pos": self.pos, "texts": self.texts, "points_colors": self.points_colors}))

    def remove_vertex(self, point):
        index = int(point.index())
        self.pos = np.delete(self.pos, index, axis=0)
        self.texts.pop(index)
        self.points_colors.pop(index)

        # Удаляем все ребра, связанные с данной вершиной
        self.adjacency = np.array([edge for edge in self.adjacency if index not in edge])

        # Обновляем индексы в ребрах после удаления вершины
        self.adjacency = np.array([[i if i < index else i - 1 for i in edge] for edge in self.adjacency])

        # Обновляем граф
        self.setData(**(self.data | {"adj": self.adjacency, "pos": self.pos, "texts": self.texts,
                                     "points_colors": self.points_colors}))

    def recolor_vertex(self, point, color):
        index = int(point.index())

        # Обновляем цвет вершины
        self.points_colors[index] = color
        self.setData(**(self.data | {"points_colors": self.points_colors}))

    def highlight_path(self, path: WeightedPath):
        if path:
            edge = None
            self.data['edgePen'] = [pg.mkPen(width=0) for _ in self.adjacency]
            for edge in path:
                self.data['symbolPen'][edge.u] = pg.mkPen(width=5, color=DARK_GREEN)
                edge_arr = np.array([edge.u, edge.v])
                edge_ind = None
                for i, row in enumerate(self.adjacency):
                    if np.array_equal(row, edge_arr):
                        edge_ind = i
                        break

                self.data['edgePen'][edge_ind] = pg.mkPen(width=5, color=DARK_GREEN)
                self.data['arrowBrush'][edge_ind] = pg.mkBrush(color=DARK_GREEN)

            self.data['symbolPen'][edge.v] = pg.mkPen(width=5, color=DARK_GREEN)
            self.updateGraph()

    def show_flags(self, line):
        line_ind = self.edges.index(line)
        start, end = self.adjacency[line_ind]
        edge = [edge for edge in self.graph.edges_of_index(int(start)) if edge.v == int(end)][0]

        self.dialog = ColorSquaresDialog(edge._flags)
        self.dialog.show()


class Worker(QThread):
    """
    Поток для выполнения фоновой задачи (здесь это time.sleep)
    """
    finished = pyqtSignal(bool, float, float, int)  # Сигнал, который передает время выполнения

    def __init__(self, graph, parent=None):
        super().__init__(parent)
        self.graph: GraphGUI = graph  # Сохранение graph как атрибута экземпляра

    def run(self):
        start_time = time.time()

        start_vertex = self.graph.graph.vertex_at(int(self.graph.start_vertex.index()))
        end_vertex = self.graph.graph.vertex_at(int(self.graph.end_vertex.index()))

        if self.graph.find_method == 'unidirectional':
            distance, path, count_op = dijkstra_unidirectional(self.graph.graph, start_vertex, end_vertex, self.graph.arc_flags)
        elif self.graph.find_method == 'bidirectional':
            distance, path, count_op = dijkstra_bidirectional(self.graph.graph, start_vertex, end_vertex, self.graph.arc_flags)

        elapsed_time = time.time() - start_time

        self.graph.highlight_path(path)

        self.finished.emit(distance != float('inf'), elapsed_time, distance, count_op)  # Эмитируем сигнал с результатом


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.graph_widget = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.graph_widget)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        self.graph = GraphGUI(self)

        self.viewbx = CustomViewBox(graph=self.graph, enableMenu=False)
        self.graph_widget.addItem(self.viewbx)
        self.viewbx.setAspectLocked()

        # Define positions of nodes
        pos = np.array([
            [0, 0],
            [10, 0],
            [0, 10],
            [10, 10],
            [5, 5],
            [15, 5]
        ], dtype=float)

        # Define the set of connections in the graph
        adj = np.array([
            [0, 1],
            [1, 0],
            [1, 3],
            [3, 2],
            [2, 0],
            [1, 5],
            [3, 5],
        ])

        # Define text to show next to each symbol
        texts = ["Point %d" % i for i in range(6)]

        points_colors = [
            (255, 255, 0),
            (255, 255, 0),
            (0, 255, 255),
            (0, 255, 255),
            (255, 0, 255),
            (255, 0, 255),
        ]

        # Update the graph
        self.graph.setData(pos=pos, adj=adj, points_colors=points_colors, texts=texts, size=1,
                           pxMode=False)
        self.initUI()

    def initUI(self):
        menubar = self.menuBar()

        # Создание меню File
        fileMenu = menubar.addMenu('Файл')

        # Добавление опции импортирования
        import_action = QAction('Импорт графа', self)
        import_action.triggered.connect(self.import_graph)
        fileMenu.addAction(import_action)

        # Добавление опции экспортирования
        export_action = QAction('Экспорт графа', self)
        export_action.triggered.connect(self.export_graph)
        fileMenu.addAction(export_action)

        # Создание меню Run
        runMenu = menubar.addMenu('Запуск')

        dijkstra_menu = QMenu("Алгоритм Дейкстры", runMenu)
        runMenu.addMenu(dijkstra_menu)

        # Добавление опций "Unidirectional" и "Bidirectional"
        unidirectional_action = QAction('Однонаправленный', self)
        unidirectional_action.triggered.connect(lambda: self.start_shortest_path('unidirectional'))
        dijkstra_menu.addAction(unidirectional_action)

        bidirectional_action = QAction('Двунаправленный', self)
        bidirectional_action.triggered.connect(lambda: self.start_shortest_path('bidirectional'))
        dijkstra_menu.addAction(bidirectional_action)

        unidirectional_action = QAction('Однонаправленный (arc_flags)', self)
        unidirectional_action.triggered.connect(lambda: self.start_shortest_path('unidirectional', True))
        dijkstra_menu.addAction(unidirectional_action)

        bidirectional_action = QAction('Двунаправленный (arc_flags)', self)
        bidirectional_action.triggered.connect(lambda: self.start_shortest_path('bidirectional', True))
        dijkstra_menu.addAction(bidirectional_action)

        self.statusBar().showMessage("")

    def start_shortest_path(self, mode, arc_flags=False):
        # Подсказка: выберите начальную вершину
        self.statusBar().showMessage("1. Выберите начальную вершину (или нажмите на поле чтобы отменить)")

        self.graph.arc_flags = arc_flags
        self.graph.find_method = mode  # Сохранение выбранного режима

    def run_algorithm(self):
        # Запуск алгоритма в отдельном потоке
        self.worker = Worker(self.graph)
        self.worker.finished.connect(self.on_algorithm_finished)  # Подключение сигнала к слоту
        self.worker.start()

    def on_algorithm_finished(self, exists, elapsed_time, distance, count_op):
        self.statusBar().showMessage("Алгоритм завершен")
        message = "Путь "
        message += "найден ✅" if exists else "не найден ❌"
        message += f".\nВремя выполнения: {elapsed_time:.5f} секунд.\n"
        message += f"Количество выполненных операций: {count_op}.\n"
        if exists:
            message += f"Расстояние пути: {distance:.2f}"
        # Показ информационного окна
        QMessageBox.information(self, "Результат", message)
        self.graph.reset_find()

    def export_graph(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.export_graph_to_json(file_name)

    def import_graph(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Graph", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.graph.setData(**(self.graph.data | self.import_graph_from_json(file_name)))

    def export_graph_to_json(self, file_path):
        graph_data = {
            "pos": self.graph.pos.tolist(),
            "adj": self.graph.adjacency.tolist(),
            "points_colors": self.graph.points_colors,
            "texts": self.graph.texts,
        }
        with open(file_path, 'w') as f:
            json.dump(graph_data, f)

    def import_graph_from_json(self, file_path):
        with open(file_path, 'r') as f:
            graph_data = json.load(f)
        graph_data['pos'] = np.array(graph_data["pos"])
        graph_data['adj'] = np.array(graph_data["adj"])
        return graph_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle('Arc Flags Visualization')
    main_window.show()
    sys.exit(app.exec())
