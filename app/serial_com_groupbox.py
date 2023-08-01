import time
import numpy as np
import serial
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

class SerialComGroupBox(QWidget):
    def __init__(self, parent: QWidget = None, fixed_size:list=[None, None]):
        super().__init__(parent)
        self.ser = serial.Serial(timeout= 0.05)
        self.serial_baudrate_ = 115200
        self.serial_port_ = 0
        self.tx_packet = [0,0,0,0,0,0,0,0,0]
        self.rx_packet = [0,0,0,0,0,0]
        # ----
        self.SerialComGroupBox = QGroupBox("Serial Com")
        self.SerialComGroupBox.setStyleSheet("background: #e6e6fa")
        if not fixed_size[0] == None:
            self.SerialComGroupBox.setFixedWidth(fixed_size[0])
        if not fixed_size[1] == None:
            self.SerialComGroupBox.setFixedHeight(fixed_size[1])
        # --- select baudrate
        baudrates_ = ["9600", "115200", "921600"]
        baudComboBox = QComboBox()
        baudComboBox.addItems(baudrates_)
        baudComboBox.setCurrentText(baudrates_[1])
        baud_label = QLabel("&Baudrate:")
        baud_label.setBuddy(baudComboBox)
        baudComboBox.activated[str].connect(self.__setSerialBaudRate)
        # --- select port
        port_spinBox = QSpinBox(self.SerialComGroupBox)
        port_spinBox.setValue(0)
        port_spinBox.setMaximum(10)
        port_label = QLabel("&Port:")
        port_label.setBuddy(port_spinBox)
        port_spinBox.valueChanged[int].connect(self.__setSerialPort)
        # --- connect and close buttons
        self.serial_connect_but = QPushButton("Connect Serial ")
        self.serial_connect_but.setCheckable(True)
        self.serial_connect_but.setChecked(False)
        self.serial_connect_but.toggled[bool].connect(self.serialConnect)
        # ---- Serial dubug display
        self.serial_debug_disp = QLabel("  Serial is not Connected ")
        self.serial_debug_disp.setStyleSheet("background-color: #ffb6c1")
        self.serial_debug_disp.setFont(QFont('Times', 10))
        # self.serial_debug_disp.setFixedSize(200, 50)
        # --- add widegets
        layout = QHBoxLayout()
        layout.addWidget(baud_label)
        layout.addWidget(baudComboBox)
        layout.addWidget(port_label)
        layout.addWidget(port_spinBox)
        layout.addWidget(self.serial_connect_but)
        layout.addWidget(self.serial_debug_disp)
        layout.addStretch(1)
        self.SerialComGroupBox.setLayout(layout)

    def serialConnect(self, connect:bool):
        """
            Only if enable to connect to serial port, all other widges will be enable.
        """
        if self.ser.is_open and not connect:
            self.ser.close()
            if self.ser.is_open:
                self.serial_debug_disp.setStyleSheet("background-color: #ffb6c1")
                self.serial_debug_disp.setText("  Failed to close serial port ")
                print("faild to close serial port")
                self.serial_connect_but.setChecked(True)
            else:
                self.serial_connect_but.setText("Connect serial")
                self.serial_debug_disp.setStyleSheet("background-color: #ffb6c1")
                self.serial_debug_disp.setText("  Serial port is closed ")
                self.serial_connect_but.setChecked(False)
                print("serial port is closed")
        
        elif not self.ser.is_open and connect:
            self.ser.baudrate = self.serial_baudrate_
            self.ser.port = f'/dev/ttyUSB{self.serial_port_}'
            try:
                self.ser.open()
                self.serial_debug_disp.setStyleSheet("background-color: #90ee90")
                self.serial_debug_disp.setText("   Serial port is connected ")
                self.serial_connect_but.setText("Disconnect serial")
                print("Serial port is conneced")
                self.enable_control_widgets = True
            except:
                self.serial_debug_disp.setStyleSheet("background-color: #ffb6c1")
                self.serial_debug_disp.setText("  Failed to connect with serial port ")
                print("Failed to connect with serial port ")
                self.serial_connect_but.setChecked(False)
                self.enable_control_widgets = False

    def __setSerialBaudRate(self, baudrate:str):
        self.serial_baudrate_ = int(baudrate)
        print(f"{self.serial_baudrate_}")
    
    def __setSerialPort(self, port:int):
        self.serial_port_ = port
        print(self.serial_port_)

    def write_serial(self, msg:list)->bool:
        """
        * msg: tx message to send over serial
        * return: 
        \t * 0: failed to send, serial is not open
        \t * 1: sent
        """
        if self.ser.is_open:
            self.ser.write(msg)
            # time.sleep(0.0004)
            return 1
        else: 
            return 0

    def read_serial(self, bytes:int)->list:
        """
        * bytes: number of bytes to read
        * return: read bytes
        """
        if self.ser.is_open:
            self.ser.flush()
            b_rx = self.ser.read(bytes)
            return b_rx
        else:
            return None
            

    