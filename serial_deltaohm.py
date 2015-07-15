# use serial port COM11 for delta instrument
# send 'HA\r\n'
# read Date=2014/09/22 14:44:52;   622;     0;   49.8;   23.3;   999;  ERR. ;  ERR. ;  ERR. ;   12.3;   10.4;    8.9;   16.5;   46.0
# 33 symbols is enough

import serial
import traceback
import time
from comm_modbus2 import *

a=4.1 # kordaja  niiskuse  y=ax+b
b=-520  # nihe
c=0.5 # temp moju

d= 33.5 # co2 kordaja
e= -650 # nihe
f= -9.3 # temp komp
g= -1.8 # niiskuse komp

mb=CommModbus(port='COM26')

ser = serial.Serial(timeout=1)
ser.baudrate = 460800
ser.port = 'COM11'
ser.open()


with open('climate.log','a') as logfile:
    logfile.write('\r\n'+'CO2, RH, T, co1, co2, cot, rh1, rh2, rht, time, rhcalc, cocalc, airh, aico2'+'\n')
    print('CO2, RH, T, co1, co2, cot, rh1, rh2, rht, time, rhcalc, cocalc')
    
print(ser)
print(mb)
print('starting endless loop, use ctrl+c to break...')

stop = 0
while stop == 0:
    out=[0,0,0,0,0,0,0,0,0,0,0,0] # 9 members
    try: # to prevent stopping in case of error
        s=ser.write('HA\r') # CR needed
        time.sleep(0.5)
        s=ser.readline()
        if len(s) < 100: # powered down?
            stop=1
            print('no deltaohm response, exiting')
            
        s2=s[25:55]
        out[0]=int(float(s2[0:6])) # co2 ppm
        out[1]=int(10*float(s2[16:21])) # RH d%
        out[2]=int(10*float(s2[23:29])) # T ddegC
        #print('deltaohm', out) #debug
        
        inn=mb.read(1,700,8)
        ainn=mb.read(1,2,2) # hum ja co2
        #print('mb inn',inn, 'ainn', ainn) #debug
        
        co=inn[0:4] # change if needed, depends on 2438 id
        rh=inn[4:8]
        #print('rh',rh,'co',co) #debug
        
        out[3]=co[0] # direct co2 sensor output
        out[4]=co[1] # differential co2 sensor output
        if out[4] > 32767:
            out[4]=out[4] - 65536
        out[5]=int(round(co[3]/25.6,0)) # co2 sensor temp ddegC
       
        out[6]=rh[0] # direct rh sensor output
        out[7]=rh[1] # differential rh sensor output
        if out[7] > 32767:
            out[7]=out[7] - 65536
        
        out[8]=int(round(rh[3]/25.6,0)) # rh sensor temp ddegC
       
        out[9]=int(time.time())  # in seconds
        out[10]=int(round((out[6]*a+b+out[8]*c), 0)) # calculated rh using a, b, c 
        out[11]=int(round((out[3]*d+e+out[8]*f+out[10]*g), 0)) # calculated co2 using t and calc rh
        
        out.append(ainn[0]) # temporary ai hum sensor output, 4V scale
        out.append(ainn[1]) # temporary ai co2 sensor output, 4 V scale = 4095
        
        # do not use diff out for now, nonlinear!
        
        with open('climate.log','a') as logfile:
            logfile.write(str(out).strip('[').strip(']')+'\n')
            print(str(out).strip('[').strip(']'))
        #print(s2,out)
        #print('CO2, RH, T, co1, co2, cot, rh1, rh2, rht, time',out)
    except:
        traceback.print_exc()
    time.sleep(10) # interval between readings
    
print('stopped')
    