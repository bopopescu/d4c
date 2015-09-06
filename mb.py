#mb.py - using pymodbus in serial mode to read and write modbus command. only for linux!
# parameters mba regadd count  to read
# parameters mba regadd hexdata to write (1 register only)

# only for archlinux and only for 1 or 2 registers write at this stage
# selle too ajal ei tasu muid sama seriali kasutavaid asju kaimas hoida!
# 04.03.2014 kasutusele minimalmodbus.


#import time
#import datetime
#import decimal
import sys
import traceback
#import subprocess
#from socket import *
#import select
#import string
import minimalmodbus # kohendatud debug-variant python3 jaoks olinuxinole!

cmd=0

argnum=len(sys.argv)
#print(sys.argv,'arg count',argnum) # debug
mba=int(sys.argv[1]) # mb aadress

client = minimalmodbus.Instrument('/dev/ttyAPP0', mba)
client.debug = True # valjastab saadetu ja saadu hex stringina, base64 abil


regaddr=int(sys.argv[2]) #  dec! # regaddrh=format("%04x" % int(sys.argv[1])) # parameetriks dec kujul aadress, register-1!
if len(sys.argv[3]) == 4: # tundub et on hex data 1 registri jaoks (4 kohta)
    regcount=int(sys.argv[3],16) # data, hex kujul
    print('writing single register data',regcount) # ajutine
    cmd=6
elif len(sys.argv[3]) == 8: # 2 registrit korraga (8 kohta)
    regcount=(0xffff & int(sys.argv[3],16))
    cmd=10
else: # voib olla reg arv?
    if len(sys.argv[3]) <3: # ilmselt reg arv, lugemine
        regcount=int(sys.argv[3]) # loetavate reg arv
        if argnum == 5:
            if sys.argv[4] == 'i': # input register
                print('reading',regcount,'input registers starting from',regaddr) # ajutine
                cmd=4
            elif sys.argv[4] == 'h': # holding register
                print('reading',regcount,'holding registers starting from',regaddr) # ajutine
                cmd=3
            elif sys.argv[4] == 'c': # coils
                print('reading',regcount,'coils starting from',regaddr) # ajutine
                cmd=1
            else:
                print('unknown parameter',sys.argv[4])
        else:
            print('reading',regcount,'holding registers starting from',regaddr) # ajutine
            cmd=3
    else:
        print('invalid length '+str(len(sys.argv[3]))+' for parameter 3!')


output=''

#try:  #  while 1:
if cmd == 3: # lugemine, n registrit jarjest
    print('mba',mba,'regaddr',regaddr,'regcount',regcount,'cmd',cmd) # debug
    result=client.read_registers(regaddr,regcount)  # esimene on algusaadress, teine reg arv. fc 03
    print(result)
    
elif cmd == 4: # lugemine, n registrit jarjest
    print('mba',mba,'regaddr',regaddr,'regcount',regcount,'cmd',cmd) # debug
    result=client.read_registers(regaddr,regcount,functioncode=4)  # esimene on algusaadress, teine reg arv. fc 04
    print(result)
    
elif cmd == 1: # lugemine, n coils jarjest
    print('mba',mba,'regaddr',regaddr,'regcount',regcount,'cmd',cmd) # debug
    
elif cmd == 6: # kirjutamine, 1 register
    print('mba',mba,'regaddr',regaddr,'data',regcount,'cmd',cmd) # debug
    #client.write_register(address=regaddr, value=regcount, unit=mba) # only one regiter to write here
    client.write_register(regaddr,regcount)  #  value dec, fc 06
    print('ok')

elif cmd == 10: # kirjutamine, 2 registrit
    print('mba',mba,'regaddr',regaddr,'data',regcount,'cmd',cmd) # debug
    #client.write_registers(address=regaddr, values=[hidata,lodata], unit=mba) # only one regiter to write here
    client.write_long(regaddr,regcount)
    print('ok')  # not yet implemented')
else:
    print('failure, unknown function code',cmd)
