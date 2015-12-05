#check onewire id/s from 650 and 750

import sys
import traceback
import minimalmodbus # kohendatud debug-variant python3 jaoks olinuxinole!
from droidcontroller.util_n import UN

mba=int(sys.argv[1]) # mb aadress, no more arguments needed

client = minimalmodbus.Instrument('/dev/ttyAPP0', mba)
client.debug = False # True # valjastab saadetu ja saadu hex stringina, base64 abil

regcount = 36

for regadd in [650, 750]: # ds18b20 ja ds2438
    result = client.read_registers(regadd,regcount)  # esimene on algusaadress, teine reg arv. fc 03
    res = UN.onewire_hexid(result)
    print(regadd, res)