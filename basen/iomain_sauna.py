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

import os, sys, time, traceback
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
        self.footwarning = 0
        self.chlevel = 0
        self.panelpower = 0
        self.ledstates = [0, 0, 0, 0]
        self.fdvalue = 777
        self.ts_gps = time.time()
        print('ControllerApp instance created')

    def app(self, appinstance):
        ''' customer-specific things, like lighting control '''
        ts_app = time.time()
        res= 0
        footwarning = 0
        shvalue = None
        values = None
        voltage = None
        chlevel = 0
        
        di = d.get_divalues('DIW')
        do = d.get_divalues('DOW')
        log.info('di: '+str(di)+', do: '+str(do)) ##

        # switch on panelpower if any of led strips ios on
        # switch off panelpower if all led strips are on
        # switch panel temporarely on if car connected or disconnected

        try:
            if self.di != None and di != self.di: # only changes
                ledsum = 0
                for i in range(4):
                    if di[i] != self.di[i] and di[i] == 0: # change, press start
                        led[i].toggle()
                    ledstate = led[i].get_state()
                    if ledstate[0] != self.ledstates[i]:
                        log.info('light '+str(i + 1)+' new state '+str(ledstate[0]))
                        self.ledstates[i] = ledstate[0]
                    d.set_dovalue('LTW', i+1, ledstate[0]) # actual output service, fixed in dchannels.py 13.9.2015
                    ledsum += ledstate[0]
                
            ## DATA FOR seneca S401 panel rows / via aochannels! panel update ##
            for i in range(7): # panel values 7 rows
                if i == 0: # sauna temp
                    aivalue = ac.get_aivalue('T1W', 1)[0] # can be None! sauna
                elif i == 1: # bath
                    aivalue = ac.get_aivalue('T2W', 1)[0] # panel row 2 bath
                elif i == 2: # outdoor
                    aivalue = ac.get_aivalue('T3W', 1)[0] # panel row 3
                elif i == 3: # hotwater
                    aivalue = ac.get_aivalue('T4W', 1)[0] # panel row 4

                elif i == 4: # battery
                    batt_presence = ac.get_aivalues('BPW') # car and batt voltage presence
                    voltage = ac.get_aivalues('BTW') # panel row 5, sauna battery
                    shvalue = voltage[1] # sauna batt
                    if voltage != None and voltage[0] != None and voltage[1] != None and voltage[0] > voltage[1] + 10 and voltage[0] > 13200: # recharging possible
                        if voltage[0] > voltage[1] + 1000: # low current initially
                            chlevel = 1
                        elif voltage[0] < voltage[1] + 500: # directly together
                            chlevel = 2
                    else:
                        chlevel= 0 # no car voltage present or engine stopped

                    #log.info('batt charging level '+str(chlevel)+', voltages '+str(voltage)) ##
                    if chlevel != self.chlevel:
                        log.info('NEW batt charging level '+str(chlevel)+', voltages '+str(voltage)) 
                        d.set_dovalue('BCW', 1, (chlevel & 1)) # via resistor
                        d.set_dovalue('BCW', 2, (chlevel & 2) >> 1)
                        self.chlevel = chlevel


                elif i == 5: # feet and door chk via AI1. values 3600, 3150, 2580
                    aivalue = ac.get_aivalue('A1V',1)[0] # ai1 voltage 0..4095 mV, pullup 1 k on
                    if aivalue != None:
                        fdvalue=777 # initially
                        if aivalue < 100: # all ok, foot down, door closed
                            fdvalue = 0 # ok, panel row 6
                        else:
                            if aivalue > 3700:
                                log.warning('feet/door line cut!')
                                fdvalue = 990
                            elif aivalue > 2400 and aivalue < 2800:
                                fdvalue = 1
                            elif aivalue > 2800 and aivalue < 3300:
                                fdvalue = 2
                            elif aivalue > 3300 and aivalue < 3700:
                                fdvalue = 3
                            elif aivalue < 1000:
                                fdvalue = 0 # ok
                        #log.info('feet/door aivalue '+str(aivalue)+', shvalue '+str(fdvalue)) ##
                        if fdvalue != self.fdvalue:
                            d.set_divalue('FDW',1,(fdvalue & 1))
                            d.set_divalue('FDW',2,(fdvalue & 2) >> 1)
                            log.info('NEW feet/door aivalue '+str(aivalue)+', fdvalue '+str(fdvalue))
                            self.fdvalue = fdvalue
                        shvalue = (fdvalue & 1)

                            
                elif i == 6: # door
                    shvalue = (self.fdvalue & 2) >> 1 # door bit in self.dvalue
                    
                #######
                            
                if i < 4:  # temperatures
                    if aivalue != None:
                        shvalue = int(round(aivalue / 10.0, 0))
                        
                if shvalue != None: # set the aovalues for panel rows in aochannels table
                    #ac.set_aosvc('PNW', i + 1, shvalue) # panel row register write in aochannels
                    ac.set_aivalue('PNW', i + 1, shvalue) # panel row register content to monitor
                    log.debug('PNW.'+str(i + 1)+' '+str(shvalue))
                #log.info('panel row loop end')
                # panel row loop end

            values = d.get_divalues('LTW') # do1..do4
            log.info('values from LTW '+str(values))
            if values != None and len(values) > 0:
                shvalue = 0
                for j in range(len(values)):
                    shvalue += values[j] << j
                
                if shvalue > 0:
                    panelpower = 1
                else:
                    panelpower = 0
                    
                if panelpower != self.panelpower:
                    log.info('NEW panelpower '+str(panelpower))
                    self.panelpower = panelpower
                    
            else:
                log.warning('LTW values strange: '+str(values))
                
            d.set_dovalue('PPS',1,self.panelpower)
            d.sync_do() # actual output writing
            self.di = di
            ac.sync_ao()
            print('app panelpower '+str(self.panelpower)) ##
            ##  end panel update ##

            if gps and ts_app > self.ts_gps + 30:
                coord = gps.get_coordinates()
                if coord != None and coord[0] != None and coord[1] != None:
                    ac.set_airaw('G1V',1,int(coord[0] * 1000000)) # lat
                    ac.set_airaw('G2V',1,int(coord[1] * 1000000)) # lng
                else:
                    log.warning('NO coordinates from GPS device, coord '+str(coord))
                self.ts_gps = ts_app
        except:
            print('main app ERROR')
            traceback.print_exc()
        
        print('### main app end ###'+str(self.panelpower)) ####### app end ####
        

cua = CustomerApp() # test like cua.ca.udp_sender()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on

