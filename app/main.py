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


import time
import numpy as np
import serial
import sys, os


from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMenu, QMenuBar)

from serial_com_groupbox import SerialComGroupBox
from motor_control_params_panel_groupbox import MotorControlPanelTabs
from motor_serial_can_interface_groupbox import MotorSerialCanInterface
from plot_graphs_groupbox import PlotGraphsGroupBox
from data_display_groupbox import DataDisplayWidget


basedir = os.path.dirname(__file__)


class MainWindow(QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # ---
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.originalPalette = QApplication.palette()
     
        self.initUI()
        self.setWindowTitle("Mini-Cheetah Motor Driver API")

        

    def initUI(self):
        # ---
        self.serial_com_groupbox = SerialComGroupBox(self, fixed_size=[580,70])
        # ---
        self.motor_control_panel_groupbox = MotorControlPanelTabs(self, fixed_size=[None, None], min_size=[None, 100])
        self.motor_params = self.motor_control_panel_groupbox.motor_params
        # ---
        self.motor_serial_can_interface_groupbox = MotorSerialCanInterface(self.serial_com_groupbox, 
                                                                           serial=self.serial_com_groupbox.ser,
                                                                           motor_params=self.motor_params,
                                                                           fixed_size=[None, None])
        # ---
        tx_data = self.motor_serial_can_interface_groupbox.tx_packet
        rx_data = self.motor_serial_can_interface_groupbox.rx_packet
        self.data_display_groupbox_tabs = DataDisplayWidget(self, tx_data=tx_data, rx_data=rx_data,
                                                            params=self.motor_params ,min_size=[600, 200])
        # ---
        self.plot_graphs_groupbox = PlotGraphsGroupBox(self, motor_params=self.motor_params, 
                                                       rx_data=rx_data, min_size=[None, 400])
       
        # ---
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.serial_com_groupbox.SerialComGroupBox,        0, 0, 1, 1)
        mainLayout.addWidget(self.motor_control_panel_groupbox.tabs,            1, 0, 4, 1)
        mainLayout.addWidget(self.motor_serial_can_interface_groupbox.GroupBox, 5, 0, 1, 1)

        mainLayout.addWidget(self.plot_graphs_groupbox.tabs,                0, 1, 4, 1)
        mainLayout.addWidget(self.data_display_groupbox_tabs.GroupBox,                   4, 1, 2, 1)
        
        # mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        # mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

 
        
        

        # ---
    #     self.serial_com_groupbox.serial_connect_but.toggled[bool].connect(self.enable_panels)
    #     self.motor_control_panel_groupbox.tabs.setEnabled(False)
    #     self.motor_serial_can_interface_groupbox.GroupBox.setEnabled(False)
    #     self.plot_graphs_groupbox.GroupBox.setEnabled(False)

    # def enable_panels(self, enable:bool):
    #     if not self.serial_com_groupbox.ser.is_open:
    #         self.motor_control_panel_groupbox.tabs.setEnabled(False)
    #         self.motor_serial_can_interface_groupbox.GroupBox.setEnabled(False)
    #         self.plot_graphs_groupbox.GroupBox.setEnabled(False)
    #     else:
    #         self.motor_control_panel_groupbox.tabs.setEnabled(True)
    #         self.motor_serial_can_interface_groupbox.GroupBox.setEnabled(True)
    #         self.plot_graphs_groupbox.GroupBox.setEnabled(True)


# =================================================================================






# ================================================================================
if __name__  == "__main__":
    app = QApplication([])
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "../images/minicheetah_api_panel.png")))
    win = MainWindow()
    screen_h = app.desktop().screenGeometry().height()
    screen_w = app.desktop().screenGeometry().width()
    app_h = win.height()
    app_w = win.width()
    win.setMinimumSize(screen_w-50, screen_h-80)
    win.show()
    sys.exit(win.exec_())
    