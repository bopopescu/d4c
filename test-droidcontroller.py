#!/usr/bin/python3

#host='176.124.247.38' # Tipo
host='10.0.0.188' # neeme
port='10502'
pic=1

import sys
sys.path.append('./pymodbus')

##########################################################################
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient

class ToggleLED:

    def __init__(self, host, port, mba):
        self.led = 0
        self.client = ModbusClient(host=host, port=port)
        #self.lient = ModbusClient(method='rtu', stopbits=1, bytesize=8, parity='E', baudrate=19200, timeout=0.2, port='/dev/ttyAPP0')
        self.mba = mba

    def toggle(self):
        self.led = (self.led & 0x7fff) | (~self.led & 0x8000)
        #led = ~led & 0xffff
        self.client.write_register(address=0, value=self.led, unit=self.mba)
    
##########################################################################

from pymodbus.register_read_message import *

from droidcontroller.indata import InData
from droidcontroller.comm_modbus import CommModbus

import time



def cb(name, action, **kwargs):
    print(action + "(" + name + ")")
    try:
        print("  new data = " +  str(indata.read(name)))
    except Exception:
        pass

    try:
        print("  old data = " +  str(indata.read_old(name)))
    except Exception:
        print("new data")
    if (action == 'onChange'):
        if (name == 'lyliti loendur'):
            led.toggle()

def cb_temp(name, action, **kwargs):
    if (action != 'onError'):
        print("TEMP " + name + " = " + indata.read(name)['value'][0])
    else:
        print("TEMP " + name + " ERROR")



led=ToggleLED(host, port, pic)

indata = InData() # intisialiseeritakse ja kasutatakse yhte

comm = CommModbus(host=host, port=port, indata=indata)
#comm = CommModbus(port='/dev/ttyAPP0', method='rtu', stopbits=1, bytesize=8, parity='E', baudrate=19200, timeout=0.2, indata=indata)

comm.add_poll(0.2, name='lyliti loendur', statuscb=cb, convertcb=None, mba=pic, reg=413, count=1)

comm.add_poll(1, name='DO0', statuscb=cb, mba=pic, reg=0, count=1)

from droidcontroller.convert import Convert
converter = Convert()
comm.add_poll(1, name='DI1', statuscb=converter.convert, mba=pic, reg=1, count=1)

for reg in range(2, 10, 1):
    comm.add_poll(1, name='AI' + str(reg), mba=pic, reg=reg, count=2, statuscb=cb)

import droidcontroller.convert_ds18b20
ds18b20 = droidcontroller.convert_ds18b20.ConvertDS18B20()
for reg in range(600, 609, 1):
    comm.add_poll(2, name='TI' + str(reg), mba=pic, reg=reg, count=1, statuscb=cb_temp, convertcb=ds18b20.convert)

import droidcontroller.convert_ip
ip = droidcontroller.convert_ip.ConvertIP()
comm.add_poll(10, name='lanip', mba=255, reg=313, count=2, convertcb=ip.convert, statuscb=cb)


#from droidcontroller.comm_system import CommSystem
#comm_s = CommSystem(indata=indata)
#comm_s.add_poll(1, name='CPU', statuscb=cb)
#comm_s.add_poll(1, name='VM', statuscb=cb)

from droidcontroller.webserver import WebServer
w = WebServer(indata=indata)
w.daemon = True
w.start()

try:
    while True:
        time.sleep(1)

except (KeyboardInterrupt, SystemExit):
    print("try to stop thread")
    print("indata = " + str(indata))

    print(str(comm.scheduler))
    comm.__del__()
    w.stop()
