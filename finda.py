#check a range of addresses for modbus addresses, all with register address 1.
# usage: python COM31 3 22
# or python /dev/ttyUSB0 7 8
# neeme nov 2014

import sys, time
port=sys.argv[1] # /dev/ttyUSB0 voi COM31 vms
from comm_modbus3 import *
m=CommModbus(port=port)
time.sleep(1)

try:
    amin = int(sys.argv[2])
except:
    amin=1
    print('starting from modbus address',amin)


try:
    amax = int(sys.argv[3])
except:
    amax=247
    print('ending with modbus address',amax)


for a in range(amax+1-amin):
    try:
        res=m.read(amin+a,1,1)
        print(amin+a,'### success on first try! result',res)
    except:
        try:
            res=m.read(amin+a,1,1)
            print(amin+a,'### success on second try! result',res)
        except:
            print(amin+a,'no response')
