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
        self.ts_gps = time.time()
        print('ControllerApp instance created')
        
    def app(self, appinstance):
        ''' customer-specific things, like lighting control '''
        ts_app = time.time()
        res= 0
        footwarning = 0
        shvalue = None
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
            for i in range(4):
                if di[i] != self.di[i] and di[i] == 0: # change, press start
                    led[i].toggle()
                ledstate = led[i].get_state()
                if ledstate[0] != self.ledstates[i]:
                    log.info('light '+str(i + 1)+' new state '+str(ledstate[0]))
                    self.ledstates[i] = ledstate[0]
                d.set_dovalue('LTW', i+1, ledstate[0]) # actual output service, fixed in dchannels.py 13.9.2015
            
            if ledstate == [0, 0, 0, 0]:
                self.panelpower = 0 # turn off to save 50 mA
            else: 
                self.panelpower = 1 # turn panel on together with any LED
            d.set_dovalue('PPS',1,self.panelpower)
            d.sync_do() # actual output writing    
            
        ## DATA FOR seneca S401 panel rows / via aochannels! panel update ##
        for i in range(7): # panel values 7 rows
            if i == 0: # sauna temp
                aivalue = ac.get_aivalue('T1W', 1)[0] # can be None!
            elif i == 1: # bath
                aivalue = ac.get_aivalue('T2W', 1)[0] # panel row 2
            elif i == 2: # outdoor
                aivalue = ac.get_aivalue('T3W', 1)[0] # panel row 3
            elif i == 3: # hotwater
                aivalue = ac.get_aivalue('T4W', 1)[0] # panel row 4
            
            elif i == 4: # battery
                shvalue = ac.get_aivalue('BTW', 2)[0] # panel row 5, sauna battery
            
            elif i == 5: # feet and door chk via AI1. values 3150, 2650
                aivalue = ac.get_aivalue('A1V',1)[0] # ai1 voltage 0..4095 mV, pullup 1 k on
                if aivalue != None:    
                    if aivalue < 100: # all ok, foot down, door closed
                        shvalue = 0 # ok, panel row 6
                    else:
                        if aivalue > 3400: 
                            log.warning('feet/door line cut!')
                            shvalue = 990
                        elif aivalue > 2500 and aivalue < 2800:
                            shvalue = 1
                        elif aivalue > 2900 and aivalue < 3300:
                            shvalue = 3
                        elif aivalue < 1000:
                            shvalue = 0 # ok
                    d.set_divalue('FDW',1,(0 & 1))
                    d.set_divalue('FDW',2,(0 & 2))
            
            elif i == 6: # lights
                values = d.get_divalues('LTW') # do1..do4
                if values != None and type(values) == 'list':    
                    shvalue = 0
                    for j in range(len(values)):
                        shvalue += values[i] << i
            else:
                pass
                
            if i < 4:
                if aivalue != None:
                    shvalue = int(round(aivalue / 10.0, 0)) 
            if shvalue != None:
                ac.set_aosvc('PNW', i + 1, shvalue) # panel row register write in aochannels
                log.info('PNW.'+str(i + 1)+' '+str(shvalue))
            else:
                log.warning('i '+str(i)+' shvalue None!')
                
        self.di = di
        ac.sync_ao()
        ##  end panel update ##
        
        if gps and ts_app > self.ts_gps + 30:
            coord = gps.get_coordinates()
            if coord != None and coord[0] != None and coord[1] != None:
                ac.set_airaw('G1V',1,int(coord[0] * 1000000)) # lat
                ac.set_airaw('G2V',1,int(coord[1] * 1000000)) # lng
            else:
                log.warning('NO coordinates from GPS device, coord '+str(coord))
            self.ts_gps = ts_app
        ##### app end ####    
    

cua = CustomerApp() # test like cua.ca.udp_sender()
    
if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on

