import sys
import time

import numpy as np
from PyQt5 import QtCore

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
import matplotlib.transforms as transforms

from pylustrator.drag_helper import DragManager
from pylustrator.matplotlibwidget import MatplotlibWidget


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.canvas = MatplotlibWidget(self)
        self.fig = self.canvas.figure
        self.fig.number = 1


        layout.addWidget(self.canvas)

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





    def mouse_move_event(self, event):
        if self.drag is not None:
            pos = np.array([event.x, event.y])
            offset = pos - self.drag
            offset[1] = -offset[1]
            self.moveCanvasCanvas(*offset)
        trans = transforms.Affine2D().scale(2.54, 2.54) + self.fig.dpi_scale_trans.inverted()
        pos = trans.transform((event.x, event.y))
        # self.footer_label.setText("%.2f, %.2f (cm) [%d, %d]" % (pos[0], pos[1], event.x, event.y))
        #
        # if event.ydata is not None:
        #     self.footer_label2.setText("%.2f, %.2f" % (event.xdata, event.ydata))
        # else:
        #     self.footer_label2.setText("")

    def scroll_event(self, event):
        if self.control_modifier:
            new_dpi = self.fig.get_dpi() + 10 * event.step

            self.fig.figure_dragger.select_element(None)

            pos = self.fig.transFigure.inverted().transform((event.x, event.y))
            pos_ax = self.fig.transFigure.transform(self.fig.axes[0].get_position())[0]

            self.fig.set_dpi(new_dpi)
            self.fig.canvas.draw()

            self.canvas.updateGeometry()
            w, h = self.canvas.get_width_height()
            self.canvas_container.setMinimumSize(w, h)
            self.canvas_container.setMaximumSize(w, h)

            pos2 = self.fig.transFigure.transform(pos)
            diff = np.array([event.x, event.y]) - pos2

            pos_ax2 = self.fig.transFigure.transform(self.fig.axes[0].get_position())[0]
            diff += pos_ax2 - pos_ax
            self.moveCanvasCanvas(*diff)

            bb = self.fig.axes[0].get_position()

    def button_press_event(self, event):
        if event.button == 2:
            self.drag = np.array([event.x, event.y])

    def canvas_key_press(self, event):
        if event.key == "control":
            self.control_modifier = True

    def canvas_key_release(self, event):
        if event.key == "control":
            self.control_modifier = False

    def button_release_event(self, event):
        if event.button == 2:
            self.drag = None


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
