import os
import numpy as np

import matplotlib.transforms as transforms
from matplotlib.figure import Figure
from qtpy import QtWidgets, QtGui

try:  # for matplotlib > 3.0
    from matplotlib.backends.backend_qtagg import (FigureCanvas as Canvas, NavigationToolbar2QT as NavigationToolbar)
except ModuleNotFoundError:
    from matplotlib.backends.backend_qt5agg import (FigureCanvas as Canvas, NavigationToolbar2QT as NavigationToolbar)



class ToolBar(QtWidgets.QToolBar):

    def __init__(self, canvas: Canvas, figure: Figure):
        """ A widget that displays a toolbar similar to the default Matplotlib toolbar (for the zoom and pan tool)

        Args:
            canvas: the canvas of the figure
            figure: the figure
        """
        super().__init__()
        self.canvas = canvas
        self.fig = figure
        self.navi_toolbar = NavigationToolbar(self.canvas, self)
        self.navi_toolbar.hide()

        self._actions = self.navi_toolbar._actions
        self._actions["home"] = self.addAction(self.navi_toolbar._icon("home.png"), "", self.navi_toolbar.home)

        self._actions["back"] = self.addAction(self.navi_toolbar._icon("back.png"), "", self.navi_toolbar.back)

        self._actions["forward"] = self.addAction(self.navi_toolbar._icon("forward.png"), "", self.navi_toolbar.forward)
        self.addSeparator()

        # the action group makes the actions exclusive, you
        # can't use 2 at the same time
        action_group = QtWidgets.QActionGroup(self)

        self._actions["drag"] = self.addAction(self.icon("arrow.png"), "", self.setSelect)
        self._actions["drag"].setCheckable(True)
        self._actions["drag"].setActionGroup(action_group)

        self._actions["pan"] = self.addAction(self.navi_toolbar._icon("move.png"), "", self.setPan)
        self._actions["pan"].setCheckable(True)
        self._actions["pan"].setActionGroup(action_group)

        self._actions["zoom"] = self.addAction(self.navi_toolbar._icon("zoom_to_rect.png"), "", self.setZoom)
        self._actions["zoom"].setCheckable(True)
        self._actions["zoom"].setActionGroup(action_group)

        self.navi_toolbar._active = 'DRAG'
        self._actions['drag'].setChecked(True)
        self.prev_active = 'DRAG'

    def icon(self, name: str):
        """ get an icon with the given filename """
        pm = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "..","icons", name))
        if hasattr(pm, 'setDevicePixelRatio'):
            try:  # older mpl < 3.5.0
                pm.setDevicePixelRatio(self.canvas._dpi_ratio)
            except AttributeError:
                pm.setDevicePixelRatio(self.canvas.device_pixel_ratio)

        return QtGui.QIcon(pm)

    def setSelect(self):
        """ select the pylustrator selection and drag tool """
        self.fig.figure_dragger.activate()

        if self.prev_active=="PAN":
            self.navi_toolbar.pan()
        elif self.prev_active=="ZOOM":
            self.navi_toolbar.zoom()

        self.prev_active = 'DRAG'

        self.navi_toolbar._active = 'DRAG'

    def setPan(self):
        """ select the mpl pan tool """
        if self.prev_active == "DRAG":
            self.fig.figure_dragger.deactivate()

        if self.navi_toolbar._active != 'PAN':
            self.navi_toolbar.pan()

        self.prev_active = 'PAN'

    def setZoom(self):
        """ select the mpl zoom tool """
        if self.prev_active == "DRAG":
            self.fig.figure_dragger.deactivate()

        if self.navi_toolbar._active != 'ZOOM':
            self.navi_toolbar.zoom()

        self.prev_active = 'ZOOM'