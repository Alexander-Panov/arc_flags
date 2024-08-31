from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication, QDialog

from gui.config import COLORS


class ColorSquare(QWidget):
    def __init__(self, color, is_filled):
        super().__init__()
        self.color = color
        self.is_filled = is_filled
        self.setFixedSize(100, 100)  # Устанавливаем размер квадрата

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.is_filled:
            painter.setBrush(QColor(*self.color))
        else:
            painter.setBrush(Qt.GlobalColor.transparent)  # Не закрашен, если False
        painter.drawRect(0, 0, self.width(), self.height())  # Рисуем квадрат

        # Рисуем текст в центре квадрата
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.setFont(QFont('Arial', 20))
        text = '1' if self.is_filled else '0'
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


class ColorSquaresDialog(QDialog):
    def __init__(self, bool_list):
        super().__init__()
        self.setWindowTitle("Color Squares")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)  # Убираем кнопку помощи

        # Список цветов
        colors = list(COLORS.values())

        # Создаем сетку для квадратов
        layout = QGridLayout()
        layout.setSpacing(5)  # Минимальное расстояние между квадратами

        for i in range(8):
            square = ColorSquare(colors[i], bool_list[i])
            layout.addWidget(square, i // 4, i % 4)  # Располагаем квадраты в сетке 2x4

        self.setLayout(layout)
        self.adjustSize()  # Подгоняем размер окна под содержимое


if __name__ == "__main__":
    import sys

    # Список булевых переменных
    bool_list = [True, False, True, False, True, False, True, False]

    app = QApplication(sys.argv)
    dialog = ColorSquaresDialog(bool_list)
    dialog.show()
    sys.exit(app.exec())
