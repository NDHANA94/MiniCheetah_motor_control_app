from curses import baudrate
import time
from struct import *
import serial

import serial




class MotorModuleController():
    def __init__(self):

        self.ser = serial.Serial(timeout= 0.05)
        self.isSerialOpen = False

        self.rx_data = [0, 0, 0, 0, 0, 0]
        self.rx_val = [0, 0, 0, 0]
        self.tx_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    

        self.P_MAX = 12.5
        self.P_MIN = -self.P_MAX
        self.V_MAX = 65.0
        self.V_MIN = -self.V_MAX
        self.KP_MAX = 500
        self.KP_MIN = 0
        self.KD_MAX = 5
        self.KD_MIN = 0
        self.I_MAX = 40

    def connectSerial(self, baudrate = 115200, port=0):
        self.ser.baudrate = baudrate
        self.ser.port = f'/dev/ttyUSB{port}'
        try:
            self.ser.open()
            print('Serial is connected')
            return 1
        except:
            print('Could not conncet with serial. Please try again!')
            return 0

    def closeSerial(self):
        try:
            self.ser.close()
            print('Serial is closed')
            return 1
        except:
            print('could not close the serial, PLease try again!')
            return 0

    def enable_motor(self, id):
        return bytes(bytearray([id, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0XFC]))

    def disable_motor(self, id):
        return bytes(bytearray([id, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0XFD]))
  
    def set_zero(self, id):
        return bytes(bytearray([id, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE]))

    def send_cmd(self, cmd):
        if self.ser.isOpen():
            self.ser.write(cmd)
        time.sleep(0.001)

    def pack_cmd(self, id, p_des, v_des, kp, kd, i_ff):
        if p_des > self.P_MAX: p_des = self.P_MAX
        elif p_des < self.P_MIN: p_des = self.P_MIN
        if v_des > self.V_MAX: v_des = self.V_MAX
        elif v_des < self.V_MIN: v_des = self.V_MIN
        if kp > self.KP_MAX: kp = self.KP_MAX
        elif kp < self.KP_MIN: kp = self.KP_MIN
        if kd > self.KD_MAX: kd = self.KD_MAX
        elif kd<self.KD_MIN: kd = self.KD_MIN
        if i_ff > self.I_MAX: i_ff = self.I_MAX
        elif i_ff< -self.I_MAX: i_ff = -self.I_MAX
        p_des = self.float2uint(p_des, self.P_MIN, self.P_MAX, 16)
        v_des = self.float2uint(v_des, self.V_MIN, self.V_MAX, 12)
        kp = self.float2uint(kp, self.KP_MIN, self.KP_MAX, 12)
        kd = self.float2uint(kd, self.KD_MIN, self.KD_MAX, 12)
        i_ff = self.float2uint(i_ff, -self.I_MAX, self.I_MAX, 12)
        # [1] pos_High 8 bits
        # [2] pos_Low 8 bits
        # [3] vel_High 8 bits
        # [4] vel_Low 4 bits, kp_High 4 bits
        # [5] kp_Low 8 bits
        # [6] kd_High 8 bits
        # [7] kd_Low 4 bits, i_ff_High 4 bits
        # [8] i_ff_Low 8 bits
        self.tx_data[0] = id = int(id)
        self.tx_data[1] = p_des >> 8
        self.tx_data[2] = p_des&0xFF
        self.tx_data[3] = v_des>>4
        self.tx_data[4] = ((v_des&0xF)<<4) | (kp>>8)
        self.tx_data[5] = kp&0xFF
        self.tx_data[6] = kd>>4
        self.tx_data[7] = ((kd&0xF)<<4) | i_ff>>8
        self.tx_data[8] = i_ff&0xFF
        return self.tx_data
        
    def unpack_cmd(self):
        id = self.tx_data[0]
        p = self.tx_data[1]<<8 | self.tx_data[2]
        v = self.tx_data[3]<<4 | self.tx_data[4]>>4
        kp = (self.tx_data[4]&0xF)<<8 | self.tx_data[5]
        kd = self.tx_data[6]<<4 | self.tx_data[7]>>4
        i = (self.tx_data[7]&0xF)<<8 | self.tx_data[8]
        p = self.uint2float(p, self.P_MIN, self.P_MAX, 16)
        v = self.uint2float(v, self.V_MIN, self.V_MAX, 12)
        kp = self.uint2float(kp, self.KP_MIN, self.KP_MAX, 12)
        kd = self.uint2float(kd, self.KD_MIN, self.KD_MAX, 12)
        i = self.uint2float(i, -self.I_MAX, self.I_MAX, 12)
        return [id, p, v, kp, kd, i]

    def read_serial(self):
        if self.ser.isOpen():
            self.ser.flush()
            b_rx = self.ser.read(6)
            if len(b_rx) == 6:
                for i in range (len(b_rx)):
                    self.rx_data[i] = b_rx[i]        
            else:
                self.rx_data = None
        else:
            self.rx_data = None
        return self.rx_data

    def unpack_reply(self, rx_data):
        # /// 0: id
        # /// 1: [position[15-8]]
        # /// 2: [position[7-0]]
        # /// 3: [velocity[11-4]]
        # /// 4: [velocity[3-0], current[11-8]]
        # /// 5: [current[7-0]]
        if len(rx_data) == 6:
            id = rx_data[0]
            p = rx_data[1]<<8 | rx_data[2]
            v = rx_data[3]<<4 | rx_data[4]>>4
            i = (rx_data[4]&0xF)<<8 | rx_data[5]
            
            p = self.uint2float(p, self.P_MIN, self.P_MAX, 16)
            v = self.uint2float(v, self.V_MIN, self.V_MAX, 12)
            i = self.uint2float(i, -self.I_MAX, self.I_MAX, 12)
            return [id, p, v, i]
        else:
            return None

    def printInBinary(self, x):
        print("{0:b".format(x))

    def float2uint(self, x, x_min, x_max, bits):
        span = x_max - x_min
        offset = x_min
        return round((x-offset)*(float((1<<bits)-1))/span)

    def uint2float(self, x, x_min, x_max, bits):
        span = x_max - x_min
        offset = x_min
        return float(x*span/((1<<bits)-1) + offset)

    def limit_val(self, x, x_min, x_max):
        if x < x_min:
            x = x_min
        if x > x_max:
            x = x_max
        return x
    
