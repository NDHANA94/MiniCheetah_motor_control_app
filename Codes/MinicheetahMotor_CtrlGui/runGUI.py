
import PySimpleGUI as sg
from multiprocessing import Process
import threading
import numpy as np
import time


from minicheetah_motor_module import MotorModuleController


mmc = MotorModuleController()


pDes_initVal = 0.0
vDes_initVal = 0.0
kp_initVal = 100.0
kd_initVal = 3.0
i_initVal = 20.0

P_MAX = 720
V_MAX = 65
KP_MAX = 500
KD_MAX = 5
I_MAX = 40



class Data:
    def __init__(self):
        self.baudrate = 115200
        self.port = 0
        self.isSerialConnect = False
        self.isMotorEnabled = False

        self.rxValues = self.__rx_data()
        self.cmd = self.__tx_data()

        self.tx_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rx_data = None

    class __tx_data:
        def __init__(self):
            self.id = 1
            self.p = 0
            self.v = 0
            self.kp = 0
            self.kd = 0
            self.i = 0
    class __rx_data:
        def __init__(self):
            self.p = 0
            self.v = 0
            self.trq = 0

data = Data()


# CONFIG GUI
sg.theme("DarkAmber")
layout = [
            
            [sg.Text('        Mini Cheetah Motor Controller', size=(30, 2))],

            [sg.Text('==============================================================================', size=(100,1))],
            [sg.Text('Serial Connection:', size=(20, 0)), sg.Text('Baudrate:', size=(8,0)), sg.Input(f'{data.baudrate}', size=(10,0), key='baudrate'),
                                                          sg.Text('Port:', size=(5,0)), sg.Spin([0,1,2,3], 0,  size=(3,5), key='port'), 
                                                          sg.Button('Connect', size=(10,1), key='but_connect', button_color=sg.NICE_BUTTON_COLORS[1]),
                                                          sg.Button('Close', size=(10,1), key='but_close', button_color=sg.NICE_BUTTON_COLORS[2])],
            [sg.Text('==============================================================================', size=(100,1))],
            

            [sg.Text('', size=(10,1))],
            [sg.Text('P_des:', size=(10,0)), 
             sg.Slider((-P_MAX, P_MAX), orientation='h', default_value=pDes_initVal, resolution=0.1, enable_events=True, size=(70, 10), key='p_slider'), 
             sg.Input('{}'.format(pDes_initVal), size=(10,10), key='p_input') ],

            [sg.Text('V_des:', size=(10,0)), 
             sg.Slider((-V_MAX, V_MAX), orientation='h', default_value=vDes_initVal, resolution=0.1, enable_events=True, size=(70, 10), key='v_slider'), 
             sg.Input('{}'.format(pDes_initVal), size=(10,10), key='v_input') ],

            [sg.Text('kp:', size=(10,0)), 
             sg.Slider((0, KP_MAX), orientation='h', default_value=kp_initVal, resolution=0.1, enable_events=True, size=(70, 10), key='kp_slider'), 
             sg.Input('{}'.format(pDes_initVal), size=(10,10), key='kp_input') ],

            [sg.Text('kd:', size=(10,0)), 
             sg.Slider((0, KD_MAX), orientation='h', default_value=kd_initVal, resolution=0.01, enable_events=True, size=(70, 10), key='kd_slider'), 
             sg.Input('{}'.format(pDes_initVal), size=(10,10), key='kd_input') ],
            
            [sg.Text('I:', size=(10,0)), 
             sg.Slider((-I_MAX, I_MAX), orientation='h', default_value=i_initVal, resolution=0.1, enable_events=True, size=(70, 10), key='i_slider'), 
             sg.Input('{}'.format(pDes_initVal), size=(10,10), key='i_input') ],


            [sg.Text('', size=(10,1))],
            [sg.Text('============================================================================================', size=(130,1))],
            [sg.Text('                  Motor:', size=(20,0)), 
             sg.Text('         ID:', size=(8,0)), sg.Spin([x+1 for x in range (12)], 1,  size=(3,5), key='id'),
            #  sg.Text('', size=(17,0)),
             sg.Button('Enable Motor', size=(10,2), key='but_enable', button_color=('white', 'green')),
             sg.Button('Disable Motor', size=(10,2), key='but_disable', button_color=('white', 'red')),
             sg.Button('Set Zero', size=(10,2), key='but_setzero', button_color=sg.NICE_BUTTON_COLORS[0]),
             sg.Button('Send CMD', size=(10,2), key='but_sendcmd', button_color=sg.NICE_BUTTON_COLORS[5])],
            [sg.Text('============================================================================================', size=(130,1))],


            [sg.Text('', size=(10,1))],
            [sg.Text('Freq:', size=(5,0)), sg.Input('100', size=(20,0), key='freq', enable_events=True)],

            [sg.Text('Tx data in dec.:', size=(14,0)), sg.Text('', size=(35,0), key='disp_tx_dec'), sg.Text('Rx data in dec.:', size=(14,0)), sg.Text('', size=(35,0), key='disp_rx_dec')],
            [sg.Text('Tx data in hex.:', size=(14,0)), sg.Text('', size=(35,0), key='disp_tx_hex'), sg.Text('Rx data in hex.:', size=(14,0)), sg.Text('', size=(35,0), key='disp_rx_hex')],

            [sg.Text('', size=(10,2))],
            [sg.Output(size=(100,10), key='_output_')],

            

        ]

window = sg.Window('MINI CHEETAH MOTOR CONTROLLER', layout, finalize=True)




def runGui():
    while True:
        event, values = window.read()
        window.find_element('_output_').Update('')
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        else:
            # ================ Serial connection ====================
            if event == 'but_connect' and not data.isSerialConnect:
                data.baudrate = values['baudrate']
                data.port = int(values['port'])
                
                if mmc.connectSerial(data.baudrate, data.port):
                        window['port'].update(disabled=True)
                        data.isSerialConnect = True
                else:
                    data.isSerialConnect = False

            if event == 'but_close' and data.isSerialConnect:
                if mmc.closeSerial():
                    window['port'].update(disabled=False)
                    data.isSerialConnect = False


            # ======================= Motor ============================             
            if values['id'] != data.cmd.id:
                data.cmd.id = int(values['id'])
            if values['p_slider'] != data.cmd.p:
                data.cmd.p = float(values['p_slider'])
                window.find_element('p_input').Update('{}'.format(data.cmd.p))
            if values['v_slider'] != data.cmd.v:
                data.cmd.v = float(values['v_slider'])
                window.find_element('v_input').Update('{}'.format(data.cmd.v))
            if values['kp_slider'] != data.cmd.kp:
                data.cmd.kp = float(values['kp_slider'])
                window.find_element('kp_input').Update('{}'.format(data.cmd.kp))
            if values['kd_slider'] != data.cmd.kd:
                data.cmd.kd = float(values['kd_slider'])
                window.find_element('kd_input').Update('{}'.format(data.cmd.kd))
            if values['i_slider'] != data.cmd.i:
                data.cmd.i = float(values['i_slider'])
                window.find_element('i_input').Update('{}'.format(data.cmd.i))

            if data.isSerialConnect:
                if event == 'but_enable':
                    data.tx_data = mmc.enable_motor(data.cmd.id)
                    mmc.send_cmd(data.tx_data)
                    data.rx_data = mmc.read_serial()
                    if not data.rx_data == None and data.rx_data[0] == data.cmd.id:
                        print(f'Motor {data.cmd.id} is enabled!')
                        data.isMotorEnabled = True
                        val = mmc.unpack_reply(data.rx_data)
                        if not val == None:
                            data.rxValues.p = val[1]
                            data.rxValues.v = val[2]
                            data.rxValues.trq = val[3]
                            print(f'Motor state -> p: {data.rxValues.p} \t v: {data.rxValues.v} \t trq: {data.rxValues.trq } \n\r')
                    else:
                        print('ERROR: Motor is not connected')

                   
                if event == 'but_disable':
                    data.tx_data = mmc.disable_motor(data.cmd.id)
                    mmc.send_cmd(data.tx_data)
                    data.rx_data = mmc.read_serial()
                    if data.rx_data != None and data.rx_data[0] == data.cmd.id:
                        print(f'Motor {data.cmd.id} is disabled!')
                        data.isMotorEnabled = False
                        val = mmc.unpack_reply(data.rx_data)
                        if not val == None:
                            data.rxValues.p = val[1]
                            data.rxValues.v = val[2]
                            data.rxValues.trq = val[3]
                            print(f'Motor state -> p: {data.rxValues.p} \t v: {data.rxValues.v} \t trq: {data.rxValues.trq } \n\r')
                    else:
                        print('ERROR: Motor is not connected')


                if event == 'but_setzero' :#and not data.isMotorEnabled:
                    data.tx_data = mmc.set_zero(data.cmd.id)
                    mmc.send_cmd(data.tx_data)
                    mmc.rx_data = mmc.read_serial()
                    if data.rx_data != None and data.rx_data[0] == data.cmd.id:
                        print(f'Motor {data.cmd.id} set zero succesfully!')
                        val = mmc.unpack_reply(data.rx_data)
                        if not val == None:
                            data.rxValues.p = val[1]
                            data.rxValues.v = val[2]
                            data.rxValues.trq = val[3]
                            print(f'Motor state -> p: {data.rxValues.p} \t v: {data.rxValues.v} \t trq: {data.rxValues.trq } \n\r')
                    else:
                        print('ERROR: Could not set zero. Please check motor connection and try again!')

                # elif event == 'but_setzero' and data.isMotorEnabled:
                #     print('Please disable the motor before set zero!')

                if event == 'but_sendcmd' and data.isMotorEnabled:
                    data.tx_data = mmc.pack_cmd(data.cmd.id, data.cmd.p*np.pi/180, data.cmd.v, data.cmd.kp, data.cmd.kd, data.cmd.i)
                    mmc.send_cmd(data.tx_data)
                    data.rx_data = mmc.read_serial()
                    if data.rx_data != None and data.rx_data[0] == data.cmd.id:
                        print(f'sending cmd to Motor {data.cmd.id}')
                        val = mmc.unpack_reply(data.rx_data)
                        if not val == None:
                            data.rxValues.p = val[1]
                            data.rxValues.v = val[2]
                            data.rxValues.trq = val[3]
                            print(f'Motor state -> p: {data.rxValues.p} \t v: {data.rxValues.v} \t trq: {data.rxValues.trq } \n\r')
                    else:
                        print('ERROR: Motor is not connected')
                    
                elif event == 'but_sendcmd' and not data.isMotorEnabled:
                    print('Please enable the motor!')
                
            if not data.isSerialConnect:
                print('Serial is not connected. Please connect!')

            if not data.tx_data == None:
                window.find_element('disp_tx_dec').Update(f'{data.tx_data}')
                window.find_element('disp_tx_hex').Update('{0:X} \ {0:X} \ {0:X} \ {0:X} \ {0:X} \{0:X} \{0:X} \{0:X} \{0:X} '
                                                    .format(data.tx_data[0], data.tx_data[1], data.tx_data[2], data.tx_data[3], data.tx_data[4],
                                                            data.tx_data[5], data.tx_data[6], data.tx_data[7], data.tx_data[8]))
            if not data.rx_data == None:                                           
                window.find_element('disp_rx_dec').Update(f'{data.rx_data}')
                window.find_element('disp_rx_hex').Update('{0:X} \ {0:X} \ {0:X} \ {0:X} \ {0:X} \{0:X} '
                                                    .format(data.rx_data[0], data.rx_data[1], data.rx_data[2], data.rx_data[3], data.rx_data[4],
                                                            data.rx_data[5]))
    window.close()


def motor_rx_tx():
    if data.isSerialConnect and data.isMotorEnabled:
        pass




def main(args=None):
    print("Starting...")
    runGui()



if __name__ == '__main__':
    main()