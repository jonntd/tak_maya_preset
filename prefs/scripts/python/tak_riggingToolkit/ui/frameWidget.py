"""
Custom Qt framewidget similar maya frame widget.
"""

from Qt import QtWidgets, QtCore, QtGui


class FrameWidget(QtWidgets.QGroupBox):
    def __init__(self, title='', parent=None):
        super(FrameWidget, self).__init__(title, parent)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 7, 0, 0)
        layout.setSpacing(0)
        super(FrameWidget, self).setLayout(layout)

        self.__widget = QtWidgets.QFrame(parent)
        self.__widget.setFrameShape(QtWidgets.QFrame.Panel)
        self.__widget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.__widget.setLineWidth(0)
        layout.addWidget(self.__widget)

        self.__collapsed = False

    def setLayout(self, layout):
        self.__widget.setLayout(layout)

    def expandCollapseRect(self):
        return QtCore.QRect(0, 0, self.width(), 20)

    def mouseReleaseEvent(self, event):
        if self.expandCollapseRect().contains(event.pos()):
            self.toggleCollapsed()
            event.accept()
        else:
            event.ignore()

    def toggleCollapsed(self):
        self.setCollapsed(not self.__collapsed)

    def setCollapsed(self, state=True):
        self.__collapsed = state

        if state:
            self.setMinimumHeight(20)
            self.setMaximumHeight(20)
            self.__widget.setVisible(False)
        else:
            self.setMinimumHeight(0)
            self.setMaximumHeight(1000000)
            self.__widget.setVisible(True)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        x = self.rect().x()
        y = self.rect().y()
        w = self.rect().width()
        offset = 25

        painter.setRenderHint(painter.Antialiasing)
        painter.fillRect(self.expandCollapseRect(), QtGui.QColor(93, 93, 93))
        painter.drawText(
            x + offset, y + 3, w, 16,
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop,
            self.title()
        )
        self.__drawTriangle(painter, x, y)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.end()

    def __drawTriangle(self, painter, x, y):
        if not self.__collapsed:
            points = [QtCore.QPoint(x + 10, y + 6),
                      QtCore.QPoint(x + 20, y + 6),
                      QtCore.QPoint(x + 15, y + 11)
                      ]

        else:
            points = [QtCore.QPoint(x + 10, y + 4),
                      QtCore.QPoint(x + 15, y + 9),
                      QtCore.QPoint(x + 10, y + 14)
                      ]

        currentBrush = painter.brush()
        currentPen = painter.pen()

        painter.setBrush(
            QtGui.QBrush(
                QtGui.QColor(187, 187, 187),
                QtCore.Qt.SolidPattern
            )
        )
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.drawPolygon(QtGui.QPolygon(points))
        painter.setBrush(currentBrush)
        painter.setPen(currentPen)
