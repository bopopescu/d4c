''' kasuta oma soovi kohaselt, muutes parameetreid.
     VAIKESTE VIIDETE JAOKS KASUTA SPETS PYMODBUS VERSIOONI ALAMKATALOOGIS pymodbus 
 '''

import time, sys
from comm_modbus3 import * # comm_modbus3.py must be present at current directory 
m = CommModbus(port='COM31') # use your port here

mba = 1 # modbus address
regaddr = 0 # register address
regcount = 10 # number of registers to query
delay = 0 # 0.025  # s between queries


if __name__ == '__main__':
    while True:  # endless loop, cancel with ctrl-c
        print(m.read(mba, regaddr, regcount)) # prints the response
        time.sleep(delay) # wait between queries
        
