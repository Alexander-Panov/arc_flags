import json
import sys

import numpy as np
import pyqtgraph as pg
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog


class Graph(pg.GraphItem):
    def __init__(self, **kwargs):
        self.textItems = []
        self.texts = []
        self.arrows = []

        super().__init__(**kwargs)
        self.points_colors = []

        self.scatter.sigClicked.connect(self.clicked)

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

    def drawArrows(self, color='w'):
        for arrow in self.arrows:
            arrow.scene().removeItem(arrow)
        self.arrows = []
        if self.adjacency is not None:
            for edge in self.adjacency:
                start = self.pos[edge[0]]
                end = self.pos[edge[1]]

                arrow = pg.ArrowItem(pos=end,
                                     angle=np.degrees(np.arctan2(-(end[1] - start[1]), end[0] - start[0])) + 180,
                                     brush=pg.mkBrush(color=color))
                self.arrows.append(arrow)
                self.getViewBox().addItem(arrow)

    def clicked(self, pts):
        print("clicked: %s" % pts)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.graph_widget = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.graph_widget)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

        self.viewbx = pg.ViewBox()
        self.graph_widget.addItem(self.viewbx)
        self.viewbx.setAspectLocked()

        self.graph = Graph()
        self.viewbx.addItem(self.graph)

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
        fileMenu = menubar.addMenu('File')

        # Добавление опции экспортирования
        export_action = QAction('Export Graph', self)
        export_action.triggered.connect(self.export_graph)
        fileMenu.addAction(export_action)

        # Добавление опции импортирования
        import_action = QAction('Import Graph', self)
        import_action.triggered.connect(self.import_graph)
        fileMenu.addAction(import_action)

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
