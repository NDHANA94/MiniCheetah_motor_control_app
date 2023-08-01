"""MIT License

Copyright (c) 2023 Nipun Dhananjaya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,)

import sys
from motor_params import MotorParams
from motor_utils import float2uint, uint2float, unpack_reply
import numpy as np
import time

from matplotlib.backends.qt_compat import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class PlotGraphsGroupBox(QWidget):
    def __init__(self, parent:QWidget, motor_params:MotorParams, rx_data:list, fixed_size:list=[None, None], min_size:list=[None, None]):
        super().__init__(parent)
        self.motor_params = motor_params
        self.rx_data = rx_data

        self.tabs = QTabWidget(self)

        if not fixed_size[0]==None:
            self.tabs.setFixedWidth(fixed_size[0])
        elif not min_size[0]==None:
            self.tabs.setMinimumWidth(min_size[0])
        if not fixed_size[1]==None:
            self.tabs.setFixedHeight(fixed_size[1])
        elif not min_size[1]==None:
            self.tabs.setMinimumHeight(min_size[1])

        
        self.p_plot_tab = PositionPlottingCanvas(self, motor_params=self.motor_params, rx_data=self.rx_data)
        self.v_plot_tab = VelocityPlottingCanvas(self, motor_params=self.motor_params, rx_data=self.rx_data)
        self.i_plot_tab = CurrentPlottingCanvas(self, motor_params=self.motor_params, rx_data=self.rx_data)
        self.tabs.addTab(self.p_plot_tab._main, "Position")
        self.tabs.addTab(self.v_plot_tab._main, "Velocity")
        self.tabs.addTab(self.i_plot_tab._main, "Current")

        self.v_plot_tab._timer.stop()
        self.i_plot_tab._timer.stop()
        

        self.tabs.currentChanged.connect(self.switch_tab)

    def switch_tab(self):
        if self.tabs.currentIndex() == 0:
            self.p_plot_tab._timer.start()
            self.v_plot_tab._timer.stop()
            self.i_plot_tab._timer.stop()
        if self.tabs.currentIndex() == 1:
            self.p_plot_tab._timer.stop()
            self.v_plot_tab._timer.start()
            self.i_plot_tab._timer.stop()
        if self.tabs.currentIndex() == 2:
            self.p_plot_tab._timer.stop()
            self.v_plot_tab._timer.stop()
            self.i_plot_tab._timer.start()



# =====================================================================================
#                            Position Ploting Tab 
# =====================================================================================
class PositionPlottingCanvas(QtWidgets.QMainWindow):
    def __init__(self, parent:QWidget, motor_params:MotorParams, rx_data:list=[]):
        super().__init__()
        self.parent = parent
        self.tx = motor_params
        self.rx_p = rx_data
        self.y = []
        self.dt = 100 # ms
        self.plot_x_min = -10
        self.plot_x_max = 0
        self.plot_samples = int(10000/self.dt+1)
        self.plot_y_min = -np.pi
        self.plot_y_max = np.pi
        self.prev_t = None
        # --------------------------------------------
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        # initialize canvas for dynamic plotting with a navigation tool bar
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.nav_toolbar = NavigationToolbar(dynamic_canvas, self)
        layout.addWidget(dynamic_canvas)
        layout.addWidget(self.nav_toolbar)
        # initialize a subplot
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax.set_ylim(self.tx.p_des.min_value-0.1, self.tx.p_des.max_value+0.1)
        self._dynamic_ax.set_xlim(self.plot_x_min, self.plot_x_max)
        self._dynamic_ax.grid()
        # initialize p_tx_line plot line
        self._x = np.linspace(self.plot_x_min, self.plot_x_max, self.plot_samples)
        self._y_tx = [None]*self.plot_samples
        self._p_tx_line, = self._dynamic_ax.plot(self._x, self._y_tx)
        # initialize p_rx_line plot line
        self._y_rx = [None]*self.plot_samples
        self._p_rx_line, = self._dynamic_ax.plot(self._x, self._y_rx)
        # add legends
        self._dynamic_ax.legend([self._p_tx_line, self._p_rx_line], ["desired [rad]", "actual [rad]"])
        # setup timer
        self._timer = dynamic_canvas.new_timer(self.dt)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        self.y.append(self.tx.p_des.cmd)
        self._y_tx.pop(0)
        self._y_tx.append(self.tx.p_des.cmd)
        rx = unpack_reply(self.rx_p, self.tx)
        self._y_rx.pop(0)
        self._y_rx.append(rx[1])
        
        self._p_tx_line.set_data(self._x, self._y_tx)
        self._p_tx_line.figure.canvas.draw()

        self._p_rx_line.set_data(self._x, self._y_rx)
        self._p_rx_line.figure.canvas.draw()
        # print(time.time())
        


# =====================================================================================
#                            Velocity Ploting Tab 
# =====================================================================================
class VelocityPlottingCanvas(QtWidgets.QMainWindow):
    def __init__(self, parent:QWidget, motor_params:MotorParams, rx_data:list=[]):
        super().__init__()
        self.parent = parent
        self.tx = motor_params
        self.rx_p = rx_data
        self.y = []
        self.dt = 100 # ms
        self.plot_x_min = -10
        self.plot_x_max = 0
        self.plot_samples = int(10000/self.dt+1)
        self.plot_y_min = -np.pi
        self.plot_y_max = np.pi
        self.prev_t = None
        # --------------------------------------------
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        # initialize canvas for dynamic plotting with a navigation tool bar
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.nav_toolbar = NavigationToolbar(dynamic_canvas, self)
        layout.addWidget(dynamic_canvas)
        layout.addWidget(self.nav_toolbar)
        # initialize a subplot
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax.set_ylim(self.tx.v_des.min_value-0.1, self.tx.v_des.max_value+0.1)
        self._dynamic_ax.set_xlim(self.plot_x_min, self.plot_x_max)
        self._dynamic_ax.grid()
        # initialize p_tx_line plot line
        self._x = np.linspace(self.plot_x_min, self.plot_x_max, self.plot_samples)
        self._y_tx = [None]*self.plot_samples
        self._v_tx_line, = self._dynamic_ax.plot(self._x, self._y_tx)
        # initialize p_rx_line plot line
        self._y_rx = [None]*self.plot_samples
        self._v_rx_line, = self._dynamic_ax.plot(self._x, self._y_rx)
        # add legends
        self._dynamic_ax.legend([self._v_tx_line, self._v_rx_line], ["desired [rad/sec]", "actual [rad/sec]"])
        # setup timer
        self._timer = dynamic_canvas.new_timer(self.dt)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        self.y.append(self.tx.v_des.cmd)
        self._y_tx.pop(0)
        self._y_tx.append(self.tx.v_des.cmd)
        rx = unpack_reply(self.rx_p, self.tx)
        self._y_rx.pop(0)
        self._y_rx.append(rx[2])
        
        self._v_tx_line.set_data(self._x, self._y_tx)
        self._v_tx_line.figure.canvas.draw()

        self._v_rx_line.set_data(self._x, self._y_rx)
        self._v_rx_line.figure.canvas.draw()
        # print(time.time())



# =====================================================================================
#                            Current Ploting Tab 
# =====================================================================================
class CurrentPlottingCanvas(QtWidgets.QMainWindow):
    def __init__(self, parent:QWidget, motor_params:MotorParams, rx_data:list=[]):
        super().__init__()
        self.parent = parent
        self.tx = motor_params
        self.rx_p = rx_data
        self.y = []
        self.dt = 100 # ms
        self.plot_x_min = -10
        self.plot_x_max = 0
        self.plot_samples = int(10000/self.dt+1)
        self.plot_y_min = -np.pi
        self.plot_y_max = np.pi
        self.prev_t = None
        # --------------------------------------------
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        # initialize canvas for dynamic plotting with a navigation tool bar
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.nav_toolbar = NavigationToolbar(dynamic_canvas, self)
        layout.addWidget(dynamic_canvas)
        layout.addWidget(self.nav_toolbar)
        # initialize a subplot
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax.set_ylim(self.tx.i_ff.min_value-1, self.tx.i_ff.max_value+1)
        self._dynamic_ax.set_xlim(self.plot_x_min, self.plot_x_max)
        self._dynamic_ax.grid()
        # initialize p_tx_line plot line
        self._x = np.linspace(self.plot_x_min, self.plot_x_max, self.plot_samples)
        self._y_tx = [None]*self.plot_samples
        self._iff_tx_line, = self._dynamic_ax.plot(self._x, self._y_tx)
        # initialize p_rx_line plot line
        self._y_rx = [None]*self.plot_samples
        self._iff_rx_line, = self._dynamic_ax.plot(self._x, self._y_rx)
        # add legends
        self._dynamic_ax.legend([self._iff_tx_line, self._iff_rx_line], ["I_ff [A]", "motor current [A]"])
        # setup timer
        self._timer = dynamic_canvas.new_timer(self.dt)
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        self.y.append(self.tx.i_ff.cmd)
        self._y_tx.pop(0)
        self._y_tx.append(self.tx.i_ff.cmd)
        rx = unpack_reply(self.rx_p, self.tx)
        self._y_rx.pop(0)
        self._y_rx.append(rx[3])
        
        self._iff_tx_line.set_data(self._x, self._y_tx)
        self._iff_tx_line.figure.canvas.draw()

        self._iff_rx_line.set_data(self._x, self._y_rx)
        self._iff_rx_line.figure.canvas.draw()
        # print(time.time())