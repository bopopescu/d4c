APVER='ioloop app basen 09.2015'
''' highest level script for basen sauna app 
from iomain_sauna import * # testing
cua.ca.di_reader(); d.get_chg_dict(); d.sync_do(); mb[0].read(1,0,2)
cua.ca.app('test')

####
while True:
    cua.ca.di_reader()
    d.get_chg_dict()
    cua.ca.app('test')
    time.sleep(1)


'''
# FIXME - uuestikaivitusel loe ja sailita reg0 senine seis!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import * 
from droidcontroller.statekeeper import * 
from droidcontroller.read_gps import * #
gps = ReadGps(speed = 4800) # USB

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

led = [] # lighting instances
for i in range(4): # button triggers
    led.append(StateKeeper(off_tout = 3600, on_tout = 0))

class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''
        self.ca = ControllerApp(self.app)
        self.di = None
        self.lights = [0, 0, 0, 0] # do1...do4
        self.footwarning = 0
        print('ControllerApp instance created. ac, d: '+str(ac)+', '+str(d))
        
    def app(self, appinstance):
        ''' customer-specific things, like lighting control '''
        res= 0
        footwarning = 0
        value = None
        values = None
        #print('iomain.sauna.app execution')
        di = d.get_divalues('DIW')
        do = d.get_divalues('DOW')
        log.info('di: '+str(di)+', do: '+str(do)) ##
        self.panelpower = 0
        self.ledstates = [0, 0, 0, 0]
        
        # switch on panelpower if any of led strips ios on
        # switch off panelpower if all led strips are on
        # switch panel temporarely on if car connected or disconnected
        
        if self.di != None and di != self.di: # only changes
            for i in range(8):
                if i <= 4: # proxy buttons
                    if di[i] != self.di[i] and di[i] == 0: # change, press start
                        led[i].toggle()
                        #self.lights[i] = (1 ^ self.lights[i])
                    ledstate = led[i].get_state()
                    if ledstate[0] != self.ledstates[i]:
                        log.info('light '+str(i + 1)+' new state '+str(ledstate[0]))
                        self.ledstates[i] = ledstate[0]
                    d.set_dovalue('LTW', i+1, ledstate[0]) # actual output service, fixed in dchannels.py 13.9.2015
                    ##s.setbit_do(1, state, 1, 0) # bit, value, mba, regadd, mbi=0 # ei toimi!
                    #s.setby_dimember_do('LTW', i + 1, state)
                    d.sync_do() # actual output writing
                        
                        
                if i >= 5 and i <= 8: # levels checked. feet 
                    if di[i] == 1: # foot up
                        footwarning = 1
                    self.footwarning = footwarning # 0 is ok
            
        #coord = gps.read() # 2 members in list
        #ca.ac.set_aivalues('GPW', values = coord)
        
        #writing seneca S401 panel rows
        for i in range(7): # panel values 7 rows
            if i == 0: # sauna temp
                pass #value = ac.get_aivalue('T1W',1) # get_aivalue(svc,member)
            elif i == 1: # bath
                pass #value = ac.get_aivalue('T2W',1) # get_aivalue(svc,member)
            elif i == 2: # outdoor
                pass #value = ac.get_aivalue('T3W',1) # get_aivalue(svc,member)
            elif i == 3: # hotwater
                pass #value = ac.get_aivalue('T4W',1) # get_aivalue(svc,member)
            elif i == 4: # battery
                pass #value = ac.get_aivalue('BTW',1) # get_aivalue(svc,member)
            
            elif i == 5: # feetok
                values = d.get_divalues('DIW')[4:8] # di5...di8
                if values != None and type(values) == 'list':    
                    value = 0
                    for j in range(len(values)):
                        value += values[i] << i
                    ac.set_aovalue(value, 1, 1000 + i) # send to panel
                    
            elif i == 6: # lights
                values = d.get_divalues('LTW') # do1..do4
                if values != None and type(values) == 'list':    
                    value = 0
                    for j in range(len(values)):
                        value += values[i] << i
                    ac.set_aovalue(value, 1, 1000 + i) # send to panel
                    
        self.di = di

        coord = gps.get_coordinates()
        if coord != None and coord[0] != None and coord[1] != None:
            ac.set_airaw('G1V',1,int(coord[0] * 1000000)) # lat
            ac.set_airaw('G2V',1,int(coord[1] * 1000000)) # lng
        else:
            log.warning('no coordinates from GPS device, coord '+str(coord))
        ##### app end ####    
    

cua = CustomerApp() # test like cua.ca.udp_sender()
    
if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on

