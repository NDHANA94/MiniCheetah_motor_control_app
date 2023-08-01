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

import typing
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem,  QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFrame)
import json
import os
import time

import numpy as np
from motor_params import MotorParams
from motor_utils import float2uint, uint2float, unpack_reply


class DataDisplayWidget(QWidget):
    def __init__(self, parent:QWidget, tx_data:list, rx_data:list, params:MotorParams,  fixed_size:list=[None, None], min_size:list=[None, None]):
        super().__init__(parent)
        self.tx_data = tx_data
        self.rx_data = rx_data
        self.params = params
        self.disp_update_timer = QTimer()
        self.disp_update_timer.timeout.connect(self.__timer_callback)
        self.disp_update_timer.setInterval(10)
        

        self.GroupBox = QGroupBox("Data Display")
        if not fixed_size[0]== None:
            self.GroupBox.setFixedWidth(fixed_size[0])
        elif not min_size[0] == None:
            self.GroupBox.setMinimumWidth(min_size[0])
        if not fixed_size[1]== None:
            self.GroupBox.setFixedHeight(fixed_size[1])
        elif not min_size[1] == None:
            self.GroupBox.setMinimumHeight(min_size[1])

        self.create_UI()
        self.disp_update_timer.start()

    def create_UI(self):
        self.layout_ = QGridLayout()
        # create tx raw data display
        self.__create_tx_display(0, 0)
        self.__create_rx_display(0, 1)

        self.GroupBox.setLayout(self.layout_)

    def __create_tx_display(self, r, c):
        tx_layout = QGridLayout()
        tx_layout.addWidget(QLabel("\t\t~Tx Data~"), 0, 0, 1, 4)
        # create raw data hbox layout
        layout1 = QHBoxLayout()
        label2 = QLabel("Raw:")
        label2.setFont(QFont("Times", 10))
        # labels for data value
        self.raw_tx = [QLabel("None") for _ in range(9)]
        layout1.addWidget(label2)
        for i in range(9):
            self.raw_tx[i].setStyleSheet("background-color: #7AC5CD")
            self.raw_tx[i].setAlignment(Qt.AlignCenter)
            self.raw_tx[i].setFont(QFont("Times", 10))
            self.raw_tx[i].setFixedSize(30,20)
            layout1.addWidget(self.raw_tx[i])
        tx_layout.addLayout(layout1, r+1, c)
        #  create decimal tx data display layout
        layout2 = QGridLayout()
        name_list = ["id:", "p_des:", "v_des:", "kp:", "kd:", "i_ff:"]
        name_labels = [QLabel("") for _ in range(6)]
        for i in range(len(name_labels)):
            name_labels[i].setText(name_list[i])
            name_labels[i].setFixedSize(35, 15)
            name_labels[i].setFont(QFont("Times", 10))
            layout2.addWidget(name_labels[i], i, 0, 1, 1)
        # set value labels
        self.tx_val = [QLabel("None") for _ in range(6)]
        for i in range(len(self.tx_val)):
            self.tx_val[i].setFixedSize(40, 15)
            self.tx_val[i].setAlignment(Qt.AlignCenter)
            self.tx_val[i].setFont(QFont("Times", 10))
            layout2.addWidget(self.tx_val[i],   i, 1, 1, 2)
        tx_layout.addLayout(layout2, r+2, c)
        # add tx layout to groupbox layout
        self.layout_.addLayout(tx_layout, r, c)
    
    def __create_rx_display(self, r, c):
        rx_layout = QGridLayout()
        rx_layout.addWidget(QLabel("\t\t~Rx Data~"), 0, 0, 1, 4)
        # create raw data hbox layout
        layout1 = QHBoxLayout()
        label2 = QLabel("Raw:")
        label2.setFont(QFont("Times", 10))
        # labels for data value
        self.raw_rx = [QLabel("None") for _ in range(6)]
        layout1.addWidget(label2)
        for i in range(6):
            self.raw_rx[i].setStyleSheet("background-color: #7AC5CD")
            self.raw_rx[i].setAlignment(Qt.AlignCenter)
            self.raw_rx[i].setFont(QFont("Times", 10))
            self.raw_rx[i].setFixedSize(30,20)
            layout1.addWidget(self.raw_rx[i])
        rx_layout.addLayout(layout1, r+1, c)
        #  create decimal tx data display layout
        layout2 = QGridLayout()
        name_list = ["id:", "p:", "v:", "i:"]
        name_labels = [QLabel("") for _ in range(4)]
        for i in range(len(name_labels)):
            name_labels[i].setText(name_list[i])
            name_labels[i].setFixedSize(20, 15)
            name_labels[i].setFont(QFont("Times", 10))
            layout2.addWidget(name_labels[i], i, 0, 1, 1)
        # set value labels
        self.rx_val = [QLabel("None") for _ in range(4)]
        for i in range(len(self.rx_val)):
            self.rx_val[i].setFixedSize(40, 15)
            self.rx_val[i].setAlignment(Qt.AlignHCenter)
            self.rx_val[i].setFont(QFont("Times", 10))
            layout2.addWidget(self.rx_val[i],   i, 1, 1, 3)
        # add vertical spaces to balance with tx side
        for i in range(2):
            rx_layout.addWidget(QLabel(), 4+i, 0, 1, 1)
        # ---
        rx_layout.addLayout(layout2, r+2, c)
        # add tx layout to groupbox layout
        self.layout_.addLayout(rx_layout, r, c)


    def __timer_callback(self):
        # print(self.tx_data)
        self.__update_data()

    def __update_data(self):
        # update tx raw data
        for i in range(len(self.tx_data)):
            self.raw_tx[i].setText(str(self.tx_data[i]))

        # update tx decimal values
        self.tx_val[0].setText(str(self.tx_data[0]))
        self.tx_val[1].setText(str(round(self.params.p_des.cmd, 4)))
        self.tx_val[2].setText(str(round(self.params.v_des.cmd, 4)))
        self.tx_val[3].setText(str(round(self.params.kp.cmd, 4)))
        self.tx_val[4].setText(str(round(self.params.kd.cmd, 4)))
        self.tx_val[5].setText(str(round(self.params.i_ff.cmd, 4)))

        # update rx raw data
        for i in range(len(self.rx_data)):
            self.raw_rx[i].setText(str(self.rx_data[i]))
        
        # update rx deciaml values
        rx_val = unpack_reply(self.rx_data, self.params)

        self.rx_val[0].setText(str(self.rx_data[0]))
        self.rx_val[1].setText(str(round(rx_val[1],4)))
        self.rx_val[2].setText(str(round(rx_val[2],4)))
        self.rx_val[3].setText(str(round(rx_val[3],4)))


