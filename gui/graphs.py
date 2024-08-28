import json
import sys

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QAction, QPixmap, QColor, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMenu


class CustomViewBox(pg.ViewBox):
    def __init__(self, graph, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.addItem(self.graph)


class Graph(pg.GraphItem):
    def __init__(self, **kwargs):
        self.textItems = []
        self.texts = []
        self.arrows = []
        self.edges = []  # Список графических элементов рёбер

        super().__init__(**kwargs)
        self.points_colors = []

        self.dragging_edge = False  # Флаг, показывающий, что идёт добавление ребра
        self.start_vertex = None  # Начальная вершина для ребра
        self.temp_arrow = None  # Временная стрелка, которую пользователь тянет
        self.temp_line = None

        self.scatter.sigClicked.connect(self.scatter_right_click)

    def setData(self, **kwargs):
        self.data = kwargs
        self.texts = self.data.pop('texts', [])
        self.points_colors = self.data.pop('points_colors', [])
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        if self.points_colors:
            self.data['symbolBrush'] = [pg.mkBrush(color=color) for color in self.points_colors]
            self.data['symbolPen'] = [pg.mkPen(width=0) for _ in self.points_colors]
        self.data['pen'] = pg.mkPen(width=5)
        self.setTexts(self.texts)
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
        self.drawArrows()

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
            ind = pts[0].data()[0]
            self.dragOffset = self.pos[ind] - pos
        if ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        self.updateGraph()
        ev.accept()

    def hoverEvent(self, ev):
        if self.dragging_edge and self.temp_arrow:
            # Обновление временной стрелки, которая следует за курсором
            self.update_temp_line_arrow(ev.pos())

    def mouseClickEvent(self, ev):
        if self.dragging_edge:
            self.finish_adding_edge(None)

    def drawArrows(self, color='w'):
        for arrow in self.arrows:
            arrow.scene().removeItem(arrow)
        self.arrows = []
        if self.adjacency is not None:
            for edge in self.adjacency:
                start = self.pos[edge[0]]
                end = self.pos[edge[1]]

                arrow = pg.ArrowItem(pos=end,
                                     angle=np.degrees(np.arctan2((end[1] - start[1]), end[0] - start[0])) + 180,
                                     brush=pg.mkBrush(color=color),
                                     headLen=0.7,
                                     pxMode=False)
                self.arrows.append(arrow)
                self.getViewBox().addItem(arrow)

    def scatter_right_click(self, scatter, points, event):
        if points and self.dragging_edge:
            self.finish_adding_edge(points[0])
        elif points and not self.dragging_edge:
            context_menu = QMenu()
            # Действие "Удалить вершину"
            delete_action = QAction("Удалить вершину", context_menu)
            delete_action.triggered.connect(lambda: self.remove_vertex(points[0]))
            context_menu.addAction(delete_action)

            # Действие "Перекрасить вершину"
            color_menu = QMenu("Перекрасить вершину", context_menu)
            context_menu.addMenu(color_menu)

            # Добавление опций цветов в подменю
            colors = {
                'Красный': (255, 0, 0),
                'Зеленый': (0, 255, 0),
                'Синий': (0, 0, 255),
                'Голубой': (0, 255, 255),
                'Розовый': (255, 0, 255),
                'Желтый': (255, 255, 0),
                'Черный': (0, 0, 0),
                'Белый': (255, 255, 255)
            }

            for color_name, rgb in colors.items():
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
        angle = np.degrees(
            np.arctan2((end_pos.y() - start_pos.x()), end_pos.x() - start_pos.y())) + 180
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

    def add_edge(self, start_vertex, end_vertex):
        start_index = int(start_vertex.data()[0])
        end_index = int(end_vertex.data()[0])

        # Проверка, что такое ребро еще не существует
        if not any((edge == [start_index, end_index]).all() for edge in self.adjacency):
            self.adjacency = np.vstack([self.adjacency, [start_index, end_index]])
            self.setData(pos=self.pos, adj=self.adjacency, points_colors=self.points_colors, texts=self.texts, size=1,
                         pxMode=False)

    def remove_vertex(self, point):
        index = int(point.data()[0])
        self.pos = np.delete(self.pos, index, axis=0)
        self.texts.pop(index)
        self.points_colors.pop(index)

        # Удаляем все ребра, связанные с данной вершиной
        self.adjacency = np.array([edge for edge in self.adjacency if index not in edge])

        # Обновляем индексы в ребрах после удаления вершины
        self.adjacency = np.array([[i if i < index else i - 1 for i in edge] for edge in self.adjacency])

        # Обновляем граф
        self.setData(pos=self.pos, adj=self.adjacency, points_colors=self.points_colors, texts=self.texts, size=1,
                     pxMode=False)

    def recolor_vertex(self, point, color):
        index = int(point.data()[0])

        # Обновляем цвет вершины
        self.points_colors[index] = color
        self.setData(pos=self.pos, adj=self.adjacency, points_colors=self.points_colors, texts=self.texts, size=1,
                     pxMode=False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.graph_widget = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.graph_widget)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        self.graph = Graph()

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

        # Add context menu
        self.graph_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.graph_widget.customContextMenuRequested.connect(self.show_context_menu)

    def initUI(self):
        menubar = self.menuBar()

        # Создание меню File
        fileMenu = menubar.addMenu('File')

        # Добавление опции экспортирования
        export_action = QAction('Export Graph', self)
        export_action.triggered.connect(self.export_graph)
        fileMenu.addAction(export_action)

        # Добавление опции импортирования
        import_action = QAction('Import Graph', self)
        import_action.triggered.connect(self.import_graph)
        fileMenu.addAction(import_action)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)

        # Add vertex action
        add_vertex_action = QAction('Добавить вершину', self)
        add_vertex_action.triggered.connect(lambda: self.add_vertex(pos))
        context_menu.addAction(add_vertex_action)

        context_menu.exec(self.mapToGlobal(pos))

    def add_vertex(self, pos):
        view_pos = self.viewbx.mapSceneToView(QPointF(pos))
        new_pos = np.array([view_pos.x(), view_pos.y()])

        # Add new position to the existing ones
        self.graph.pos = np.vstack([self.graph.pos, new_pos])

        # Optionally, add a default text and color for the new vertex
        self.graph.texts.append(f"Point {len(self.graph.pos) - 1}")
        self.graph.points_colors.append((255, 255, 255))  # Default color (white)

        # Update the graph with the new vertex
        self.graph.setData(pos=self.graph.pos, adj=self.graph.adjacency, points_colors=self.graph.points_colors,
                           texts=self.graph.texts, size=1, pxMode=False)

    def export_graph(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.export_graph_to_json(file_name)

    def import_graph(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Graph", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            pos, adj, points_colors, texts = self.import_graph_from_json(file_name)
            self.graph.setData(pos=pos, adj=adj, points_colors=points_colors, texts=texts, pxMode=False)

    def export_graph_to_json(self, file_path):
        graph_data = {
            "positions": self.graph.pos.tolist(),
            "adjacency": self.graph.adjacency.tolist(),
            "points_colors": self.graph.points_colors,
            "texts": self.graph.texts,
        }
        with open(file_path, 'w') as f:
            json.dump(graph_data, f)

    def import_graph_from_json(self, file_path):
        with open(file_path, 'r') as f:
            graph_data = json.load(f)
        pos = np.array(graph_data["positions"])
        adj = np.array(graph_data["adjacency"])
        points_colors = graph_data['points_colors']
        texts = graph_data["texts"]
        return pos, adj, points_colors, texts


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle('Arc Flags Visualization')
    main_window.show()
    sys.exit(app.exec())
