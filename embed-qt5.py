import os
import sys
import time

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from matplotlib import _pylab_helpers, transforms

from pylustrator.components.align import Align
from pylustrator.components.plot_layout import ToolBar
from pylustrator.drag_helper import DragManager
from pylustrator.matplotlibwidget import MatplotlibWidget


class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.canvas_canvas = self._main
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = MatplotlibWidget(self)
        _pylab_helpers.Gcf.set_active(self.canvas.manager)
        self.fig = self.canvas.figure
        layout.addWidget(self.canvas)

        self.x_scale = QtWidgets.QLabel(self.canvas)
        self.y_scale = QtWidgets.QLabel(self.canvas)

        self.toolbar = ToolBar(self.canvas, self.fig)
        layout.addWidget(self.toolbar)


        Align(layout, self.fig) # The ctrl and shift keys are switched

        np.random.seed(1)
        t = np.arange(0.0, 2, 0.001)
        y = 2 * np.sin(np.pi * t)
        a, b = np.random.normal(loc=(5., 3.), scale=(2., 4.), size=(100, 2)).T
        b += a

        ax1 = self.canvas.figure.add_subplot(131)
        ax1.plot(t, y)

        ax2 = self.canvas.figure.add_subplot(132)
        ax2.plot(a, b, "o")

        ax3 = self.canvas.figure.add_subplot(133)
        ax3.bar(0, np.mean(a))
        ax3.bar(1, np.mean(b))
        DragManager(self.fig)
        self.fig.figure_dragger.on_select = self.wrap(self.fig.figure_dragger.on_select)
        self.updateRuler()

    def wrap(self, func):
        def newfunc(element, event=None):
            self.axes_select(element)
            return func(element, event)

        return newfunc

    def axes_select(self, element):
        print(element)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.fig.figure_dragger.selection.clear_targets()
        self.fig.figure_dragger.selected_element = None
        self.fig.figure_dragger.on_select(None, None)
        self.fig.figure_dragger.figure.canvas.draw()
        self.updateRuler()

    def showEvent(self, event):
        self.updateRuler()


    def updateRuler(self):
        trans = transforms.Affine2D().scale(1. / 2.54, 1. / 2.54) + self.fig.dpi_scale_trans
        l = 17
        l1 = 13
        l2 = 6
        l3 = 4

        w = self.canvas.width()
        h = self.canvas.height()

        self.pixmapX = QtGui.QPixmap(w, l)
        self.pixmapY = QtGui.QPixmap(l, h)

        self.pixmapX.fill(QtGui.QColor("#f0f0f0"))
        self.pixmapY.fill(QtGui.QColor("#f0f0f0"))

        painterX = QtGui.QPainter(self.pixmapX)
        painterY = QtGui.QPainter(self.pixmapY)

        painterX.setPen(QtGui.QPen(QtGui.QColor("black"), 1))
        painterY.setPen(QtGui.QPen(QtGui.QColor("black"), 1))

        offset = self.canvas.pos().x()
        start_x = np.floor(trans.inverted().transform((-offset, 0))[0])
        end_x = np.ceil(trans.inverted().transform((-offset + w, 0))[0])
        dx = 0.1
        for i, pos_cm in enumerate(np.arange(start_x, end_x, dx)):
            x = (trans.transform((pos_cm, 0))[0] + offset)
            if i % 10 == 0:
                painterX.drawLine(x, l - l1 - 1, x, l - 1)
                text = str("%d" % np.round(pos_cm))
                o = 0
                painterX.drawText(x + 3, o, self.fontMetrics().width(text), o + self.fontMetrics().height(),
                                  QtCore.Qt.AlignLeft,
                                  text)
            elif i % 2 == 0:
                painterX.drawLine(x, l - l2 - 1, x, l - 1)
            else:
                painterX.drawLine(x, l - l3 - 1, x, l - 1)
        painterX.drawLine(0, l - 2, w, l - 2)
        painterX.setPen(QtGui.QPen(QtGui.QColor("white"), 1))
        painterX.drawLine(0, l - 1, w, l - 1)
        self.x_scale.setPixmap(self.pixmapX)
        self.x_scale.setMinimumSize(w, l)
        self.x_scale.setMaximumSize(w, l)

        # height_cm = self.fig.get_size_inches()[1]*2.45
        offset = self.canvas.pos().y() + self.canvas.height()
        start_y = np.floor(trans.inverted().transform((0, +offset - h))[1])
        end_y = np.ceil(trans.inverted().transform((0, +offset))[1])
        dy = 0.1
        for i, pos_cm in enumerate(np.arange(start_y, end_y, dy)):
            y = (-trans.transform((0, pos_cm))[1] + offset)
            if i % 10 == 0:
                painterY.drawLine(l - l1 - 1, y, l - 1, y)
                text = str("%d" % np.round(pos_cm))
                o = 0
                painterY.drawText(o, y + 3, o + self.fontMetrics().width(text), self.fontMetrics().height(),
                                  QtCore.Qt.AlignRight,
                                  text)
            elif i % 2 == 0:
                painterY.drawLine(l - l2 - 1, y, l - 1, y)
            else:
                painterY.drawLine(l - l3 - 1, y, l - 1, y)
        painterY.drawLine(l - 2, 0, l - 2, h)
        painterY.setPen(QtGui.QPen(QtGui.QColor("white"), 1))
        painterY.drawLine(l - 1, 0, l - 1, h)
        painterY.setPen(QtGui.QPen(QtGui.QColor("#f0f0f0"), 0))
        painterY.setBrush(QtGui.QBrush(QtGui.QColor("#f0f0f0")))
        painterY.drawRect(0, 0, l, l)
        self.y_scale.setPixmap(self.pixmapY)
        self.y_scale.setMinimumSize(l, h)
        self.y_scale.setMaximumSize(l, h)

        w, h = self.canvas.get_width_height()

        self.pixmap = QtGui.QPixmap(w + 100, h + 10)

        self.pixmap.fill(QtGui.QColor("transparent"))

        painter = QtGui.QPainter(self.pixmap)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#666666")))
        painter.drawRect(2, 2, w + 2, h + 2)
        painter.drawRect(0, 0, w + 2, h + 2)



if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.setWindowTitle('QMainwindow - Embed Qt5 ')
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
