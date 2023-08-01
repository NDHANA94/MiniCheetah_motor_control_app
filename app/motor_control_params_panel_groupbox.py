
import typing
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFrame)
import json
import os
import time

import numpy as np
from motor_params import MotorParams
from motor_utils import float2uint, uint2float

motor_params = MotorParams()
motor_params._load_data()

# =================================================================================================================
#                                   CONTROL AND CONFIG PARAMS TAB
# =================================================================================================================
class MotorControlPanelTabs(QWidget):
    def __init__(self, parent:QWidget, fixed_size:list=[None, None], min_size:list=[None, None]):
        super().__init__(parent)
        # argument variables
        self._fixed_size = fixed_size
        self.min_size = min_size
        # initialize tabs
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("background: #faf0e6")
        self.control_params_tab = ControlParamsGroupBoxTab(self)
        self.config_params_tab = ConfigParamsGroupBoxTab(self)
        # add tabs
        self.tabs.addTab(self.control_params_tab.control_params_tab, "control panel")
        self.tabs.addTab(self.config_params_tab.config_params_tab, "Config")
        # set size
        if not self._fixed_size[0] == None:
            self.tabs.setFixedWidth(self._fixed_size[0])
        elif not min_size[0] == None:
            self.tabs.setMinimumWidth()
        if not self._fixed_size[1] == None:
            self.tabs.setFixedHeight(self._fixed_size[1])
        elif not self.min_size[1] == None:
            self.tabs.setMinimumHeight(self.min_size[1])
        # update config params
        self.tabs.currentChanged.connect(self.control_params_tab.update_UI_params)
        self.tabs.currentChanged.connect(self.config_params_tab.update_UI)
        # set control and config parameter objects
        self.motor_params = motor_params


# =================================================================================================================
#                                   CONTROL PARAMS GROUPBOX
# =================================================================================================================
class ControlParamsGroupBoxTab(QWidget):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        # motor parameters
        self.parent_ = parent
        self.params = motor_params
        # 
        self.last_p_knob_scale = 0
        # 
        self.control_params_tab = QGroupBox(self)
        self.control_params_tab.layout = self.get_UI_layout()
        self.control_params_tab.setLayout(self.control_params_tab.layout)

    def get_UI_layout(self):
        # initialize layout
        self._layout = QGridLayout()
        # create widgets
        self.__create_load_params_button(0, 1, 1, 1)
        self.__create_save_params_button(0, 2, 1, 1)
        self.__create_set_default_params_button(0, 3, 1, 1)
        # velocity control panel
        self.__create_section_divider(2)
        self.__create_v_control_panel(3, 0)
        # kp control panel
        self.__create_section_divider(5)
        self.__create_kp_control_panel(6, 0)
        # kd control panel
        self.__create_section_divider(8)
        self.__create_kd_control_panel(9, 0)
        # i_ff control panel
        self.__create_section_divider(11)
        self.__create_iff_control_panel(12, 0)
        # position control panel
        self.__create_section_divider(14)
        self.__create_p_des_control_panel(15, 0)
        return self._layout
    
    def update_UI_params(self):
        print("updating control panle UI params")
        # v_des
        self.v_des_scrollbar.setValue(self.params.v_des.get_uint_cmd_value())
        self.v_des_scrollbar.setRange(0, self.params.v_des.get_uint_max_value())
        self.v_des_value_label.setText(str(round(self.params.v_des.cmd, 4)))
        # kp
        self.kp_scrollBar.setValue(self.params.kp.get_uint_cmd_value())
        self.kp_scrollBar.setRange(0, self.params.kp.get_uint_max_value())
        self.kp_value_label.setText(str(round(self.params.kp.cmd, 4)))
        # kd
        self.kd_scrollBar.setValue(self.params.kd.get_uint_cmd_value())
        self.kd_scrollBar.setRange(0, self.params.kd.get_uint_max_value())
        self.kd_value_label.setText(str(round(self.params.kd.cmd, 4)))
        # iff
        self.iff_scrollBar.setValue(self.params.i_ff.get_uint_cmd_value())
        self.iff_scrollBar.setRange(0, self.params.i_ff.get_uint_max_value())
        self.iff_value_label.setText(str(round(self.params.i_ff.cmd, 4)))
        # p_des
        if self.p_des_dial.value() > self.params.p_des.max_value or \
        self.p_des_dial.value() < self.params.p_des.min_value:
            self.p_des_dial.setValue(self.params.p_des.get_uint_cmd_value())
        self.p_des_dial.setRange(0, self.params.p_des.get_uint_max_value())
        self.p_des_value_label.setText(str(round(self.params.p_des.cmd, 4)))
        
    
        
    def __create_load_params_button(self, row, column, row_spane=None, column_span=None):
        self.loadParams_but = QPushButton("Load Params")
        self.loadParams_but.setCheckable(True)
        self.loadParams_but.setChecked(False)
        self.loadParams_but.toggled[bool].connect(self.__load_params_task)
        self._layout.addWidget(self.loadParams_but, row, column, row_spane, column_span)

    def __create_save_params_button(self, row, column, row_spane, column_span):
        self.save_but = QPushButton("Save Params")
        self.save_but.setCheckable(True)
        self.save_but.setChecked(False)
        self.save_but.toggled[bool].connect(self.__save_params_task)
        self._layout.addWidget(self.save_but, row, column, row_spane, column_span)
    
    def __create_set_default_params_button(self, row, column, row_spane, column_span):
        self.resetParams_but = QPushButton("Set Default")
        self.resetParams_but.setCheckable(True)
        self.resetParams_but.setChecked(False)
        self.resetParams_but.toggled[bool].connect(self.__set_default_params)
        self._layout.addWidget(self.resetParams_but,  row, column, row_spane, column_span)

    def __create_v_control_panel(self, row, column, row_spane=None, column_span=None):
        # label widget
        vDes_Label = QLabel("v_des", parent=self.control_params_tab)
        # control scrollbar widget
        self.v_des_scrollbar = QScrollBar(Qt.Horizontal, self.control_params_tab)
        self.v_des_scrollbar.setStyleSheet("background: #808080")
        self.v_des_scrollbar.setRange(0, self.params.v_des.get_uint_max_value())
        self.v_des_scrollbar.setValue(self.params.v_des.get_uint_cmd_value())
        # value display widget
        self.v_des_value_label = QLabel(f"{round(self.params.v_des.cmd, 4)}", parent=self.control_params_tab)
        # assign tasks for scrolbars
        self.v_des_scrollbar.valueChanged[int].connect(self.__change_v_des_task)
        # frame
        frame = QFrame()
        frame.Shape(QFrame.HLine)
        frame.setLineWidth(1)
        frame.setVisible(True)
        # add widgets to layout
        self._layout.addWidget(vDes_Label,                  row,    column+0,   1, 1) # 3, 0, 2, 1
        self._layout.addWidget(self.v_des_scrollbar,        row,    column+1,   1, 5)
        self._layout.addWidget(self.v_des_value_label,       row,    column+6,   1, 1)

    def __create_kp_control_panel(self, row, column, row_spane=None, column_span=None):
        # label widget
        kp_label = QLabel("kp", parent=self.control_params_tab)
        # control scrollbar widget
        self.kp_scrollBar = QScrollBar(Qt.Horizontal, self.control_params_tab)
        self.kp_scrollBar.setStyleSheet("background: #808080")
        self.kp_scrollBar.setRange(0, self.params.kp.get_uint_max_value())
        self.kp_scrollBar.setValue(self.params.kp.get_uint_cmd_value())
        # value display widget
        self.kp_value_label = QLabel(f"{round(self.params.kp.cmd, 4)}", parent=self.control_params_tab)
        # assign tasks to scrollbars
        self.kp_scrollBar.valueChanged[int].connect(self.__change_kp_task)
        # add widgets to layout
        self._layout.addWidget(kp_label,                    row,    column+0,     1, 1)
        self._layout.addWidget(self.kp_scrollBar,           row,    column+1,   1, 5)
        self._layout.addWidget(self.kp_value_label,         row,    column+6,   1, 1)

    def __create_kd_control_panel(self, row, column, row_spane=None, column_span=None):
        # label widget
        kd_label = QLabel("kd", parent=self.control_params_tab)
        # control scroll scrollbar widget
        self.kd_scrollBar = QScrollBar(Qt.Horizontal, self.control_params_tab)
        self.kd_scrollBar.setStyleSheet("background: #808080")
        self.kd_scrollBar.setRange(0, self.params.kd.get_uint_max_value())
        self.kd_scrollBar.setValue(self.params.kd.get_uint_cmd_value())
        # value display widget
        self.kd_value_label = QLabel(f"{round(self.params.kd.cmd, 4)}", parent=self.control_params_tab)
        # assign tasks to scrollbars
        self.kd_scrollBar.valueChanged[int].connect(self.__change_kd_task)
        # add widgets into layout
        self._layout.addWidget(kd_label,                    row,    column+0,     1, 1)
        self._layout.addWidget(self.kd_scrollBar,           row,    column+1,   1, 5)
        self._layout.addWidget(self.kd_value_label,         row,    column+6,   1, 1)

    def __create_iff_control_panel(self, row, column, row_spane=None, column_span=None):
        # label widget
        iff_label = QLabel("i_ff:")
        # control scrollbar widget
        self.iff_scrollBar = QScrollBar(Qt.Horizontal, self.control_params_tab)
        self.iff_scrollBar.setStyleSheet("background: #808080")
        self.iff_scrollBar.setRange(0, self.params.i_ff.get_uint_max_value())
        self.iff_scrollBar.setValue(self.params.i_ff.get_uint_cmd_value())
        # value display widget
        self.iff_value_label = QLabel(f"{round(self.params.i_ff.cmd, 4)}", parent=self.control_params_tab)
        # assign tasks to scrollbars
        self.iff_scrollBar.valueChanged[int].connect(self.__change_iff_task)
        # add widgets into layout
        self._layout.addWidget(iff_label,                   row+0,  column+0, 1, 1)
        self._layout.addWidget(self.iff_scrollBar,          row+0,  column+1, 1, 5)
        self._layout.addWidget(self.iff_value_label,        row+0,  column+6, 1, 1)

    def __create_p_des_control_panel(self, row, column, row_spane=None, column_span=None):
        # label widget
        p_des_label = QLabel("               p_des[rad]:\n\tp_des[deg]:")
        # position control dial widget
        self.p_des_dial = QDial(self.control_params_tab)
        self.p_des_dial.setNotchesVisible(True)
        self.p_des_dial.setWrapping(False)
        self.p_des_dial.setRange(0, self.params.p_des.get_uint_max_value()+1)
        self.p_des_dial.setValue(self.params.p_des.get_uint_cmd_value())
        self.p_des_dial.setSingleStep(1)
        # self.p_des_dial.setGeometry(10,10,10,10)
        self.p_des_dial.setStyleSheet("background-color: #e0ffff")
        # position up control pushbuttons
        self.p_des_up_button = QPushButton("+")
        self.p_des_up_button.setFont(QFont('None', 20))
        self.p_des_up_button.setCheckable(True)
        self.p_des_up_button.setChecked(False)
        self.p_des_up_button.setAutoRepeat(True)
        self.p_des_up_button.setStyleSheet("background-color: #76EEC6")
        self.p_des_up_button.setAutoRepeatInterval(1) # ms
        # position down control pushbuttons
        self.p_des_down_button = QPushButton("-")
        self.p_des_down_button.setFont(QFont('None', 25))
        self.p_des_down_button.setCheckable(True)
        self.p_des_down_button.setChecked(False)
        self.p_des_down_button.setAutoRepeat(True)
        self.p_des_down_button.setStyleSheet("background-color: #76EEC6")
        self.p_des_down_button.setAutoRepeatInterval(1)
        self.p_des_down_button.setAutoDefault(True)
        # zero position pushbutton
        self.p_des_zero_button = QPushButton("Zero")
        self.p_des_zero_button.setFont(QFont("None", 12))
        self.p_des_zero_button.setCheckable(True)
        self.p_des_zero_button.setChecked(False)
        self.p_des_zero_button.setStyleSheet("background-color: #E3CF57")
        self.p_des_zero_timer = QTimer()
        # up down position control interval changer
        p_des_change_label = QLabel("Interval [ms]")
        self.p_des_change_interval = QSpinBox()
        self.p_des_change_interval.setRange(0,1000)
        self.p_des_change_interval.setValue(1)
        # up down position step size
        p_des_change_stepsize_label = QLabel("step size")
        self.p_des_change_step_size = QSpinBox()
        self.p_des_change_step_size.setValue(10)
        self.p_des_change_step_size.setRange(1, 1000)
        # value display widget
        self.p_des_value_label = QLabel()
        self.p_des_value_label.setText(f"{self.params.p_des.cmd}\n{self.params.p_des.cmd*180/np.pi}")
        # assign tasks
        self.p_des_dial.valueChanged[int].connect(self.__change_p_des_task)
        self.p_des_up_button.pressed.connect(self.__increase_p_des)
        self.p_des_down_button.pressed.connect(self.__decrease_p_des)
        self.p_des_change_interval.valueChanged[int].connect(self.__set_p_des_change_interval)
        self.p_des_zero_button.toggled[bool].connect(self.__set_p_des_zero)
        self.p_des_zero_timer.timeout.connect(self.__set_p_des_zero_timer_callback)
        # add widgets into layout
        self._layout.addWidget(self.p_des_dial,                  row+0, column+0, 4, 4)
        self._layout.addWidget(p_des_label,                      row+4, column+0, 1, 1)
        self._layout.addWidget(self.p_des_value_label,           row+4, column+1, 1, 2)
        self._layout.addWidget(self.p_des_up_button,             row+1, column+5, 1, 1)
        self._layout.addWidget(self.p_des_zero_button,           row+2, column+5, 1, 1)
        self._layout.addWidget(self.p_des_down_button,           row+3, column+5, 1, 1)
        self._layout.addWidget(p_des_change_label,               row+4, column+4, 1, 1)
        self._layout.addWidget(self.p_des_change_interval,       row+4, column+5, 1, 1)
        self._layout.addWidget(p_des_change_stepsize_label,      row+5, column+4, 1, 1)
        self._layout.addWidget(self.p_des_change_step_size,      row+5, column+5, 1, 1)
        
        
    def __create_section_divider(self, row):
        self.section_divider:list[QLabel()] = []
        self.section_divider.append(QLabel())
        self.section_divider[-1].setFixedHeight(3)
        self.section_divider[-1].setStyleSheet("background-color: #708090")
        self._layout.addWidget(self.section_divider[-1], row, 0, 1, 6)
   
    # -----------------------------------------------------------------------------------

    def __load_params_task(self, load:bool):
        # TODO
        if load:
            self.loadParams_but.setChecked(False)
            self.params._load_data()
            self.update_UI_params()
            
    def __save_params_task(self, save:bool):
        # TODO
        if save:
            print("saving params...")
            self.params._save_data()
            self.save_but.setChecked(False)
            print("done")
    
    def __set_default_params(self, reset:bool):
        if reset:
            print("setting default params")
            self.resetParams_but.setChecked(False)
            self.params.__init__()
            self.p_des_dial.setValue(self.params.p_des.get_uint_cmd_value())
            self.v_des_scrollbar.setValue(self.params.v_des.get_uint_cmd_value())
            self.kp_scrollBar.setValue(self.params.kp.get_uint_cmd_value())
            self.kd_scrollBar.setValue(self.params.kd.get_uint_cmd_value())
            self.iff_scrollBar.setValue(self.params.i_ff.get_uint_cmd_value())
            print("done")

    def __change_v_des_task(self, val:int):
        self.params.v_des.set_cmd_value_from_uint(val)
        self.v_des_value_label.setText(f"{round(self.params.v_des.cmd, 4)}")

    def __change_kp_task(self, val:int):
        self.params.kp.set_cmd_value_from_uint(val)
        self.kp_value_label.setText(f"{round(self.params.kp.cmd, 4)}")

    def __change_kd_task(self, val:int):
        self.params.kd.set_cmd_value_from_uint(val)
        self.kd_value_label.setText(f"{round(self.params.kd.cmd, 4)}")

    def __change_iff_task(self, val:int):
        self.params.i_ff.set_cmd_value_from_uint(val)
        self.iff_value_label.setText(f"{round(self.params.i_ff.cmd, 4)}")

    def __change_p_des_task(self, val:int):
        self.params.p_des.set_cmd_value_from_uint(val)
        self.p_des_value_label.setText(f"{round(self.params.p_des.cmd, 4)}\n{round(self.params.p_des.cmd*180/np.pi, 4)}")
        # print(self.p_des_dial.value())
    
    def __increase_p_des(self):
        p_des = self.p_des_dial.value()
        p_des += self.p_des_change_step_size.value()
        self.p_des_dial.setValue(p_des)
        self.p_des_up_button.setChecked(False)

    def __decrease_p_des(self):
        p_des = self.p_des_dial.value()
        p_des -= self.p_des_change_step_size.value()
        self.p_des_dial.setValue(p_des)
        self.p_des_down_button.setChecked(False)

    def __set_p_des_change_interval(self, interval):
        self.p_des_up_button.setAutoRepeatInterval(interval)
        self.p_des_down_button.setAutoRepeatInterval(interval)

    def __set_p_des_zero(self, set:bool):
        if set:
            print("set_zero")
            self.pdes_zero_linspace =  np.linspace(self.p_des_dial.value(), self.params.p_des.get_uint_max_value()/2, int(self.p_des_dial.value()/self.p_des_change_step_size.value()))
            self.step_to_p_des_zero = 0
            self.p_des_zero_timer.start(self.p_des_change_interval.value())
        else:
            print("stop zero")
            self.p_des_zero_timer.stop()
            self.p_des_zero_button.setChecked(False)


    def __set_p_des_zero_timer_callback(self):
        if self.params.p_des.cmd == 0:
            self.p_des_zero_timer.stop()
            self.p_des_zero_button.setChecked(False)
        else: 
            if self.step_to_p_des_zero < len(self.pdes_zero_linspace):
                p_des = self.pdes_zero_linspace[self.step_to_p_des_zero]
                self.p_des_dial.setValue(p_des)
                self.step_to_p_des_zero +=2
            else:
                self.p_des_zero_timer.stop()
                self.p_des_zero_button.setChecked(False)
        


# =================================================================================================================
#                                CONFIG GROUPBOX
# =================================================================================================================
class ConfigParamsGroupBoxTab(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.parent_ = parent
        self.params = motor_params
        self.bits_list = ["4", "8", "12", "16", "20", "24", "28", "32"]
        # --- flags
        self.__is_pMax_mirros_pMin = True 
        self.__is_vMax_mirros_vMin = True
        self.__is_iffMax_mirrors_iffMin = True

        self.create_UI()


        
    
    def create_UI(self):
        self.config_params_tab = QGroupBox(self)
        self.config_params_tab.layout = self.create_config_groupBox_layout()
        self.config_params_tab.setLayout(self.config_params_tab.layout)

    def create_config_groupBox_layout(self):
        # min max position config
        self._layout = QGridLayout()
        self.__create_position_configs(0, 0)
        self.__create_velocity_configs(1,0)
        self.__create_kp_configs(2,0)
        self.__create_kd_configs(3,0)
        self.__create_iff_configs(4,0)
        self.__create_save_config_button(5,0)
        return self._layout

    def update_UI(self):
        # update position configs
        self.p_bits_combobox.setCurrentText(str(self.params.p_des.bits))
        self.max_p_textLine_.setText(str(self.params.p_des.max_value))
        self.min_p_textLine_.setText(str(self.params.p_des.min_value))
        # update velocity configs
        self.v_bits_combobox.setCurrentText(str(self.params.v_des.bits))
        self.max_v_textLine_.setText(str(self.params.v_des.max_value))
        self.min_v_textLine_.setText(str(self.params.v_des.min_value))
        # update kp configs
        self.kp_bits_combobox.setCurrentText(str(self.params.kp.bits))
        self.max_kp_textLine_.setText(str(self.params.kp.max_value))
        self.min_kp_textLine_.setText(str(self.params.kp.min_value))
        # update kd configs
        self.kd_bits_combobox.setCurrentText(str(self.params.kd.bits))
        self.max_kd_textLine_.setText(str(self.params.kd.max_value))
        self.min_kd_textLine_.setText(str(self.params.kd.min_value))
        # update iff configs
        self.iff_bits_combobox.setCurrentText(str(self.params.i_ff.bits))
        self.max_iff_textLine_.setText(str(self.params.i_ff.max_value))
        self.min_iff_textLine_.setText(str(self.params.i_ff.min_value))

    def __create_position_configs(self, row, column):
        # bits
        p_bits_label = QLabel("bits of position value:")
        p_bits_label.setFixedWidth(150)
        self.p_bits_combobox = QComboBox()
        self.p_bits_combobox.addItems(self.bits_list)
        self.p_bits_combobox.setFixedWidth(50)
        self.p_bits_combobox.setCurrentText(str(self.params.p_des.bits))
        # max position
        max_p_label_ = QLabel("max_position:")
        self.max_p_textLine_ = QLineEdit(f"{self.params.p_des.max_value}")
        self.max_p_textLine_.setValidator(QDoubleValidator())
        self.max_p_textLine_.setFixedWidth(150)
        # min position
        min_p_lable_ = QLabel("min_position:")
        self.min_p_textLine_ = QLineEdit(f"{self.params.p_des.min_value}")
        self.min_p_textLine_.setEnabled(False)
        self.min_p_textLine_.setFixedWidth(150)
        self.min_p_textLine_.setValidator(QDoubleValidator())
        # mirror max position to min position
        p_min_mirror_max_radioBut_ = QRadioButton("min_position=-max_position")
        p_min_mirror_max_radioBut_.setCheckable(True)
        p_min_mirror_max_radioBut_.setChecked(True)
        p_min_mirror_max_radioBut_.setAutoExclusive(False)
        # connections
        self.max_p_textLine_.textChanged[str].connect(self.__update_position_value_max_task)
        # self.min_p_textLine_.textChanged[str].connect(self.__update_position_value_min_task)
        p_min_mirror_max_radioBut_.toggled[bool].connect(self.__p_value_mirror_task)
        self.p_bits_combobox.activated[str].connect(self.__update_p_bits_task)
        # setup layout
        layout = QGridLayout()
        layout.addWidget(p_bits_label,                0, 0, 1, 1)
        layout.addWidget(self.p_bits_combobox,        0, 1, 1, 1) 
        layout.addWidget(max_p_label_,                1, 0, 1, 1)
        layout.addWidget(self.max_p_textLine_,        1, 1, 1, 1)
        layout.addWidget(min_p_lable_,                2, 0, 1, 1)
        layout.addWidget(self.min_p_textLine_,        2, 1, 1, 1)
        layout.addWidget(p_min_mirror_max_radioBut_,  0, 2, 2, 1)
        self._layout.addLayout(layout, row, column)
        
        
    def __create_velocity_configs(self, row, column):
        # bits
        v_bits_label = QLabel("bits of velocity value:")
        v_bits_label.setFixedWidth(150)
        v_bits_label.setFixedWidth(150)
        self.v_bits_combobox = QComboBox()
        self.v_bits_combobox.addItems(self.bits_list)
        self.v_bits_combobox.setCurrentText(str(self.params.v_des.bits))
        self.v_bits_combobox.setFixedWidth(50)
        # max velocity
        max_v_label_ = QLabel("max_velocity:")
        self.max_v_textLine_ = QLineEdit(f"{self.params.v_des.max_value}")
        self.max_v_textLine_.setValidator(QDoubleValidator())
        self.max_v_textLine_.setFixedWidth(150)
        # min velocity
        min_v_label_ = QLabel("min_velocity:")
        self.min_v_textLine_ = QLineEdit(f"{self.params.v_des.min_value}")
        self.min_v_textLine_.setEnabled(False)
        self.min_v_textLine_.setValidator(QDoubleValidator())
        self.min_v_textLine_.setFixedWidth(150)
        # mirror max velocity to min velocity
        vp_min_mirror_max_radioBut_ = QRadioButton("min_velocity = -max_velocity")
        vp_min_mirror_max_radioBut_.setCheckable(True)
        vp_min_mirror_max_radioBut_.setChecked(True)
        vp_min_mirror_max_radioBut_.setAutoExclusive(False)
        # connections
        self.max_v_textLine_.textEdited[str].connect(self.__update_velocity_value_max_task)
        # self.min_v_textLine_.textEdited[str].connect(self.__update_velocity_value_min_task)
        vp_min_mirror_max_radioBut_.toggled[bool].connect(self.__v_value_mirror_task)
        self.v_bits_combobox.activated[str].connect(self.__update_v_bits_task)
        # setup layout
        layout = QGridLayout()
        layout.addWidget(v_bits_label,                0, 0, 1, 1)
        layout.addWidget(self.v_bits_combobox,        0, 1, 1, 1)
        layout.addWidget(max_v_label_,                1, 0, 1, 1)
        layout.addWidget(self.max_v_textLine_,        1, 1, 1, 1)
        layout.addWidget(min_v_label_,                2, 0, 1, 1)
        layout.addWidget(self.min_v_textLine_,        2, 1, 1, 1)
        layout.addWidget(vp_min_mirror_max_radioBut_, 0, 2, 2, 1)
        self._layout.addLayout(layout, row, column)

    def __create_kp_configs(self, row, column):
        # bits
        kp_bits_label = QLabel("bits of kp value:")
        kp_bits_label.setFixedWidth(150)
        self.kp_bits_combobox = QComboBox()
        self.kp_bits_combobox.addItems(self.bits_list)
        self.kp_bits_combobox.setCurrentText(str(self.params.kp.bits))
        self.kp_bits_combobox.setFixedWidth(50)
        # max kp
        max_kp_label_ = QLabel("max_kp:")
        self.max_kp_textLine_ = QLineEdit(f"{self.params.kp.max_value}")
        self.max_kp_textLine_.setValidator(QDoubleValidator())
        self.max_kp_textLine_.setFixedWidth(150)
        # min kp
        min_kp_label_ = QLabel("min_kp:")
        self.min_kp_textLine_ = QLineEdit(f"{self.params.kp.min_value}")
        self.min_kp_textLine_.setEnabled(True)
        self.min_kp_textLine_.setValidator(QDoubleValidator())
        self.min_kp_textLine_.setFixedWidth(150)
        # connections
        self.max_kp_textLine_.textEdited[str].connect(self.__update_kp_value_max_task)
        self.min_kp_textLine_.textEdited[str].connect(self.__update_kp_value_min_task)
        self.kp_bits_combobox.activated[str].connect(self.__update_kp_bits_task)
        
        # setup layout
        layout = QGridLayout()
        layout.addWidget(kp_bits_label,           0, 0, 1, 1)
        layout.addWidget(self.kp_bits_combobox,   0, 1, 1, 1)
        layout.addWidget(max_kp_label_,           1, 0, 1, 1)
        layout.addWidget(self.max_kp_textLine_,   1, 1, 1, 1)
        layout.addWidget(min_kp_label_,           2, 0, 1, 1)
        layout.addWidget(self.min_kp_textLine_,   2, 1, 1, 1)
        layout.addWidget(QLabel(),                2, 2, 1, 1)
        self._layout.addLayout(layout, row, column)
    
    def __create_kd_configs(self, row, column):
        # bits
        kd_bits_label = QLabel("bits of kd value:")
        kd_bits_label.setFixedWidth(150)
        self.kd_bits_combobox = QComboBox()
        self.kd_bits_combobox.addItems(self.bits_list)
        self.kd_bits_combobox.setCurrentText(str(self.params.kd.bits))
        self.kd_bits_combobox.setFixedWidth(50)
        # max kd
        max_kd_label_ = QLabel("max_kd:")
        self.max_kd_textLine_ = QLineEdit(f"{self.params.kd.max_value}")
        self.max_kd_textLine_.setValidator(QDoubleValidator())
        self.max_kd_textLine_.setFixedWidth(150)
        # min kd
        min_kd_label_ = QLabel("min_kd:")
        self.min_kd_textLine_ = QLineEdit(f"{self.params.kp.min_value}")
        self.min_kd_textLine_.setEnabled(True)
        self.min_kd_textLine_.setValidator(QDoubleValidator())
        self.min_kd_textLine_.setFixedWidth(150)
        # connections
        self.max_kd_textLine_.textEdited[str].connect(self.__update_kd_value_max_task)
        self.min_kd_textLine_.textEdited[str].connect(self.__update_kd_value_min_task)
        self.kd_bits_combobox.activated[str].connect(self.__update_kd_bits_task)
        # setup layout
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(kd_bits_label,           0, 0, 1, 1)
        layout.addWidget(self.kd_bits_combobox,   0, 1, 1, 1)
        layout.addWidget(max_kd_label_,           1, 0, 1, 1)
        layout.addWidget(self.max_kd_textLine_,   1, 1, 1, 1)
        layout.addWidget(min_kd_label_,           2, 0, 1, 1)
        layout.addWidget(self.min_kd_textLine_,   2, 1, 1, 1)
        layout.addWidget(QLabel(),                2, 3, 1, 1)
        self._layout.addLayout(layout, row, column)

    def __create_iff_configs(self, row, column):
        # bits
        iff_bits_label = QLabel("bits of iff value:")
        iff_bits_label.setFixedWidth(150)
        self.iff_bits_combobox = QComboBox()
        self.iff_bits_combobox.addItems(self.bits_list)
        self.iff_bits_combobox.setCurrentText(str(self.params.i_ff.bits))
        self.iff_bits_combobox.setFixedWidth(50)
        # max iff
        max_iff_label_ = QLabel("max_iff:")
        self.max_iff_textLine_ = QLineEdit(f"{self.params.i_ff.max_value}")
        self.max_iff_textLine_.setValidator(QDoubleValidator())
        self.max_iff_textLine_.setFixedWidth(150)
        # min iff
        min_iff_label_ = QLabel("min_iff:")
        self.min_iff_textLine_ = QLineEdit(f"{self.params.i_ff.min_value}")
        self.min_iff_textLine_.setEnabled(False)
        self.min_iff_textLine_.setValidator(QDoubleValidator())
        self.min_iff_textLine_.setFixedWidth(150)
        # mirror max_iff to min_iff
        iff_min_mirror_max_radioBut_ = QRadioButton("min_iff = -max_iff")
        iff_min_mirror_max_radioBut_.setCheckable(True)
        iff_min_mirror_max_radioBut_.setChecked(True)
        iff_min_mirror_max_radioBut_.setAutoExclusive(False)
        # connections
        self.max_iff_textLine_.textEdited[str].connect(self.__update_iff_value_max_task)
        # self.min_iff_textLine_.textEdited[str].connect(self.__update_iff_value_min_task)
        iff_min_mirror_max_radioBut_.toggled[bool].connect(self.__iff_value_mirror_task)
        self.iff_bits_combobox.activated[str].connect(self.__update_iff_bits_task)
        # setup layout
        layout = QGridLayout()
        layout.addWidget(iff_bits_label,                  0, 0, 1, 1)
        layout.addWidget(self.iff_bits_combobox,          0, 1, 1, 1)
        layout.addWidget(max_iff_label_,                  1, 0, 1, 1)
        layout.addWidget(self.max_iff_textLine_,          1, 1, 1, 1)
        layout.addWidget(min_iff_label_,                  2, 0, 1, 1)
        layout.addWidget(self.min_iff_textLine_,          2, 1, 1, 1)
        layout.addWidget(iff_min_mirror_max_radioBut_,    1, 2, 2, 1)
        self._layout.addLayout(layout, row, column)
    
    def __create_save_config_button(self, row, column):
        self.save_params_but = QPushButton("Save")
        self.save_params_but.setCheckable(True)
        self.save_params_but.setChecked(False)
        self.save_params_but.toggled[bool].connect(self.__save_config_task)
        self._layout.addWidget(self.save_params_but, row+0, column+1, 1, 2)

    #--------------------------------------------------------------------------------------------------------------- 
    
    def __update_position_value_max_task(self, value:str):
        if not value == '0' or not value == '':
            self.params.p_des.max_value = float(value)
            if self.__is_pMax_mirros_pMin:
                self.params.p_des.min_value = - self.params.p_des.max_value
                self.min_p_textLine_.setText(str(self.params.p_des.min_value))

    def __update_position_value_min_task(self, value:str):
        if not value == '' and float(self.max_p_textLine_.text())>float(value):
            self.params.p_des.min_value = float(value)

    def __update_velocity_value_max_task(self, value:str):
        if not value == '0' or not value == '':
            self.params.v_des.max_value = float(value)
            if self.__is_vMax_mirros_vMin:
                self.params.v_des.min_value = - self.params.v_des.max_value
                self.min_v_textLine_.setText(str(self.params.v_des.min_value))

    def __update_velocity_value_min_task(self, value:str):
        if not value == '' and float(self.max_v_textLine_.text())>float(value):
            self.params.v_des.min_value = float(value)

    def __update_kp_value_max_task(self, value:str):
        if not value == '' and float(self.min_kp_textLine_.text())<float(value):
            self.params.kp.max_value = float(value)

    def __update_kp_value_min_task(self, value:str):
        if not value == '' and float(self.max_kp_textLine_.text())>float(value):
            self.params.kp.min_value = float(value)

    def __update_kd_value_max_task(self, value:str):
        if not value == '' and float(self.min_kd_textLine_.text())<float(value):
            self.params.kd.max_value = float(value)

    def __update_kd_value_min_task(self, value:str):
        if not value == '' and float(self.max_kd_textLine_.text())>float(value):
            self.params.kd.min_value = float(value)
    
    def __update_iff_value_max_task(self, value:str):
        if not value == '0' or not value == '':
            self.params.i_ff.max_value = float(value)
            if self.__is_iffMax_mirrors_iffMin:
                self.params.i_ff.min_value = - self.params.i_ff.max_value
                self.min_iff_textLine_.setText(str(self.params.i_ff.min_value))

    def __update_iff_value_min_task(self, value:str):
        if not value == '' and float(self.max_iff_textLine_.text())>float(value):
            self.params.i_ff.min_value = float(value)

    def __update_p_bits_task(self, bits:str):
        self.params.p_des.bits = int(bits)

    def __update_v_bits_task(self, bits:str):
        self.params.v_des.bits = int(bits)
    
    def __update_kp_bits_task(self, bits:str):
        self.params.kp.bits = int(bits)

    def __update_kd_bits_task(self, bits:str):
        self.params.kd.bits = int(bits)
    
    def __update_iff_bits_task(self, bits:str):
        self.params.i_ff.bits = int(bits)

    
    def __p_value_mirror_task(self, checked:bool):
        if checked:
            self.min_p_textLine_.setEnabled(False)
            self.__is_pMax_mirros_pMin = True
            self.min_p_textLine_.destroyed.connect(self.__update_position_value_min_task)
            self.params.p_des.min_value = -self.params.p_des.max_value
            self.min_p_textLine_.setText(f"{self.params.p_des.min_value}")
            
        else:
            self.min_p_textLine_.textChanged[str].connect(self.__update_position_value_min_task)
            self.min_p_textLine_.setEnabled(True)
            self.__is_pMax_mirros_pMin = False

    def __v_value_mirror_task(self, checked:bool):
        if checked:
            self.min_v_textLine_.setEnabled(False)
            self.__is_vMax_mirros_vMin = True
            self.min_v_textLine_.destroyed.connect(self.__update_velocity_value_min_task)
            self.params.v_des.min_value = -self.params.v_des.max_value
            self.min_v_textLine_.setText(f"{self.params.v_des.min_value}")
        else:
            self.min_v_textLine_.textChanged[str].connect(self.__update_velocity_value_min_task)
            self.min_v_textLine_.setEnabled(True)
            self.__is_vMax_mirros_vMin = False

    def __iff_value_mirror_task(self, checked:bool):
        if checked:
            self.min_iff_textLine_.setEnabled(False)
            self.__is_iffMax_mirrors_iffMin = True
            self.min_iff_textLine_.destroyed.connect(self.__update_iff_value_min_task)
            self.params.i_ff.min_value = - self.params.i_ff.max_value
            self.min_iff_textLine_.setText(f"{self.params.i_ff.min_value}")
        else:
            self.min_iff_textLine_.textChanged[str].connect(self.__update_iff_value_min_task)
            self.min_iff_textLine_.setEnabled(True)
            self.__is_iffMax_mirrors_iffMin = False
        
    def __save_config_task(self, save:bool):
        self.params._save_data()
        self.save_params_but.setChecked(False)
           
            
            

    
    
        


