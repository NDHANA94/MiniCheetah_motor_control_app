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

from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QTableView)

import serial
import sys
import time

from threading import Event

from colorama import Fore
from serial_com_groupbox import SerialComGroupBox
from motor_control_params_panel_groupbox import MotorControlPanelTabs
import numpy as np
from motor_params import MotorParams

class MotorSerialCanInterface(SerialComGroupBox):
    def __init__(self, parent:None, serial:serial.Serial, 
                 motor_params:MotorParams, 
                 fixed_size:list=[None, None]):
        super().__init__(parent)
        self.ser = serial
        self.motor_params = motor_params
        self.send_cmd_freq = 100 # Hz
        self.rx_packet = [0,0,0,0,0,0]
        self.tx_packet = [0,0,0,0,0,0,0,0,0]
        # --- flags
        self.is_motor_available = False
        self.is_motor_connected = False
        self.is_motor_enabled = False
        self.is_send_cmd_once = True
        self.is_send_cmd_enable = False
        # ----
        self.GroupBox = QGroupBox("Motor Driver Interface")
        if not fixed_size[0]==None:
            self.GroupBox.setFixedWidth(fixed_size[0])
        if not fixed_size[1]==None:
            self.GroupBox.setFixedHeight(fixed_size[1])

        self.enable_but = QPushButton("Enable")
        self.enable_but.toggled[bool].connect(self._enable_but_task)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timer_callback)
        self.init_UI()
        self.pack_tx()
    
    def _enable_but_task(self, pushed:bool):
        if pushed:
            pass


    def init_UI(self):
        # motor id label widget
        self.motor_id_label_ = QLabel("Motor ID:")
        # motor id selection spinbox widget
        self.motorIdSelection_spinBox = QSpinBox()
        self.motorIdSelection_spinBox.setRange(1,12)
        # motor enable pushbutton widget
        self.motorEnable_button = QPushButton("Enable")
        self.motorEnable_button.setCheckable(True)
        self.motorEnable_button.setChecked(False)
        self.motorEnable_button.setStyleSheet("background: #90ee90")
        self.motorEnable_button.toggled[bool].connect(self.enable_motor_button_task)
        # set zero position pushbutton widget
        self.set_zero_button = QPushButton("Set Zero")
        self.set_zero_button.setCheckable(True)
        self.set_zero_button.setChecked(False)
        self.set_zero_button.setStyleSheet("background: #48d1cc")
        self.set_zero_button.toggled[bool].connect(self.set_zero_button_task)
        # motor disable pushbutton widget
        self.motorDisable_button = QPushButton("Disable")
        self.motorDisable_button.setCheckable(True)
        self.motorDisable_button.setChecked(False)
        self.motorDisable_button.setStyleSheet("background: #f08080")
        self.motorDisable_button.setMinimumHeight(60)
        self.motorDisable_button.toggled[bool].connect(self.disable_motor_button_task)
        # send cmd pushbutton widget
        self.sendCmd_button = QPushButton("Send CMD")
        self.sendCmd_button.setCheckable(True)
        self.sendCmd_button.setChecked(False)
        self.sendCmd_button.setStyleSheet("background: #66cdaa")
        self.sendCmd_button.toggled[bool].connect(self.send_cmd_button_task)
        # send cmd once or periodically selection checkbox widget
        self.sendCmdOnce_checkBox = QCheckBox("Send once")
        self.sendCmdOnce_checkBox.setCheckable(True)
        self.sendCmdOnce_checkBox.setChecked(True)
        self.sendCmdOnce_checkBox.setWhatsThis(
            "checked->True: send commond only once when the 'send cmd' button is pressed.\
             \nchecked->False: send command periodically with given frequency after 'send cmd' button is pressed")
        self.sendCmdOnce_checkBox.toggled[bool].connect(self.set_send_cmd_once_task)#set_sendCmd_once)
        # periodicaly sending cmd frequency selection linetext widget
        cmd_freq_lable = QLabel("cmd freq:")
        cmd_freq_lable.setAlignment(Qt.AlignCenter)
        self.cmd_freq_lineedit = QLineEdit(str(self.send_cmd_freq))
        self.cmd_freq_lineedit.setValidator(QDoubleValidator())
        self.cmd_freq_lineedit.setFixedWidth(100)
        # ---
        self.motorInterfaceDebugDisplay_label = QLabel("Motor is not connected")
        self.motorInterfaceDebugDisplay_label.setFont(QFont('Times', 10))
        self.motorInterfaceDebugDisplay_label.setMinimumWidth(300)
        # ---
        layout = QGridLayout()
        layout.addWidget(self.motor_id_label_, 0, 0, 1, 1)
        layout.addWidget(self.motorIdSelection_spinBox, 0, 1, 1, 1)
        layout.addWidget(self.motorEnable_button, 0, 2, 1, 1)
        layout.addWidget(self.set_zero_button, 0, 3, 1, 1)
    
        layout.addWidget(self.sendCmdOnce_checkBox, 2, 0, 1, 1)
        layout.addWidget(cmd_freq_lable, 2, 1, 1, 1)
        layout.addWidget(self.cmd_freq_lineedit, 2, 2, 1, 1)
        layout.addWidget(self.sendCmd_button, 2, 3, 1, 1)
        
        

        layout.addWidget(self.motorDisable_button, 0, 4, 3, 2)
        layout.addWidget(self.motorInterfaceDebugDisplay_label, 8, 0, 2, 2)
        self.GroupBox.setLayout(layout)

    def _display(self, msg:str):
        self.motorInterfaceDebugDisplay_label.setText(msg)
    
    def set_zero_button_task(self, set:bool):
        """ 
        Send `set zero position` motor command over serial.\n
        """
        if self.__set_zero():
            if self.__read_motor_feedback() and self.rx_packet[0] == int(self.motorIdSelection_spinBox.value()):
                self._display("Motor current position is set to zero")
                time.sleep(1.5)
            else:
                self._display(f"Error: Motor {self.motorIdSelection_spinBox.value()} is not connected!\nFailed to set zero motor!")
        else:
            self._display("Error: Serial port is not connected!")
        self.set_zero_button.setChecked(False)

    def enable_motor_button_task(self, enable:bool):
        """ 
        Send `enable` motor command over serial.\n
        If the motor is enable, set `is_motor_enabled` flag `True`.
        """
        if self.__enable_motor():
            if self.__read_motor_feedback() and self.rx_packet[0] == int(self.motorIdSelection_spinBox.value()):
                self._display("Motor is enabled")
            else:
                self._display(f"Error: Motor {self.motorIdSelection_spinBox.value()} is not connected!\nFailed to enable motor")
        else:
             self._display("Error: Serial port is not connected!")
        self.motorEnable_button.setChecked(False)

    def disable_motor_button_task(self, disable:bool):
        """ 
        Send `disable` motor command over serial.\n
        If the motor is disabled, set `is_motor_enabled` flag `False`.
        """
        if self.__disable_motor():
            if self.__read_motor_feedback() and self.rx_packet[0] == int(self.motorIdSelection_spinBox.value()):
                self._display("Motor is disabled")
                self.is_motor_enabled = False
            else:
                self._display(f"Error: Motor {self.motorIdSelection_spinBox.value()} is not connected!\nFailed to disable motor.")
                self.is_motor_enabled = True
        else:
            self._display("Error: Serial port is not connected!")
        self.motorDisable_button.setChecked(False)

                
    def set_send_cmd_once_task(self, ischecked:bool):
        if ischecked:
            self.is_send_cmd_once=True
            self.timer.stop()
        else:
            self.is_send_cmd_once=False
        self.sendCmd_button.setChecked(False)

    def send_cmd_button_task(self, send:bool):
        """
        Send current command `tx_packet` over serial when the `send` button is pressed.
        """
        if self.is_send_cmd_once:
            self.__send_motor_cmd()
            self.sendCmd_button.setChecked(False)

        else:
            if send:
                if not int(self.cmd_freq_lineedit.text()) == 0:
                    self.timer.start(1000/int(self.cmd_freq_lineedit.text()))
                else: self._display("Error: cmd_freq is set to 0")
            else: 
                self.timer.stop()

    def _timer_callback(self):
        # print(f"{self.motor_params.p_des.cmd} {self.motor_params.v_des.cmd} {self.motor_params.kp.cmd} {self.motor_params.kd.cmd} {self.motor_params.i_ff.cmd}")
        # print(f"{self.motor_params.p_des.max_value} {self.motor_params.v_des.max_value} {self.motor_params.kp.max_value} {self.motor_params.kd.max_value} {self.motor_params.i_ff.max_value}")
        self.__send_motor_cmd()

    def __set_zero(self):
        id = int(self.motorIdSelection_spinBox.value())
        zero_cmd = bytes(bytearray([id, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE]))
        return self.write_serial(zero_cmd)

    def __enable_motor(self):
        id = int(self.motorIdSelection_spinBox.value())
        enable_cmd = bytes(bytearray([id, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0XFC]))
        return self.write_serial(enable_cmd)
 
    def __disable_motor(self):
        id = int(self.motorIdSelection_spinBox.value())
        disable_cmd = bytes(bytearray([id, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0XFD]))
        return self.write_serial(disable_cmd)

    def __send_motor_cmd(self):
        self.pack_tx()
        # if self.send_tx_(self.tx_packet):
        if self.write_serial(self.tx_packet):
            time.sleep(0.005)
            if self.__read_motor_feedback() and self.rx_packet[0] == int(self.motorIdSelection_spinBox.value()):
                self._display(f"serial_tx: {self.tx_packet}\nserial_rx: {self.rx_packet}")
            else:
                self._display(f"Error: Motor {self.motorIdSelection_spinBox.value()} is not connected! \nFailed to send cmd.")
        else:
            self._display("Error: Serial port is not connected!")
    
    def __read_motor_feedback(self):
        """ 
        Read 6 bytes of motor feedback. \n
        If the feedback from selected motor save feedback data in `rx_packet`.
        * return:
        \t * 0: Feedback is NOT received
        \t * 1: Feedback is received
        """
        rx = self.read_serial(6)
        if not rx == None and len(rx) == 6 and rx[0] == int(self.motorIdSelection_spinBox.value()):
            for i in range (len(rx)):
                self.rx_packet[i] = rx[i]
            return 1
        else:
            return 0

    def pack_tx(self):
        """
        Pack current `p_des`, `v_des`, `kp`, `kd`, `i_ff` values for selected motor id into `tx_packet`and return it.
        """
        p_des = self.motor_params.p_des.get_uint_cmd_value()
        v_des = self.motor_params.v_des.get_uint_cmd_value()
        kp = self.motor_params.kp.get_uint_cmd_value()
        kd = self.motor_params.kd.get_uint_cmd_value()
        iff = self.motor_params.i_ff.get_uint_cmd_value()
        
        # print(f"params in uint: {p_des}, {v_des}, {kp}, {kd}, {iff}")

        self.tx_packet[0] = int(self.motorIdSelection_spinBox.value())
        self.tx_packet[1] = p_des >> 8
        self.tx_packet[2] = p_des&0xFF
        self.tx_packet[3] = v_des>>4
        self.tx_packet[4] = ((v_des&0xF)<<4) | (kp>>8)
        self.tx_packet[5] = kp&0xFF
        self.tx_packet[6] = kd>>4
        self.tx_packet[7] = ((kd&0xF)<<4) | iff>>8
        self.tx_packet[8] = iff&0xFF
        return self.tx_packet

        
    def float2uint(self, x, x_min, x_max, bits):
        span = x_max - x_min
        offset = x_min
        return int((x-offset)*(float((1<<bits)-1))/span)

    def uint2float(self, x, x_min, x_max, bits):
        span = x_max - x_min
        offset = x_min
        return float(x*span/((1<<bits)-1) + offset)
    
    






        