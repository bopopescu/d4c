''' highest level script for basen sauna app '''
APVER='ioloop app basen 08.11.2015' 


import os, sys, time, traceback

#sys.path.append('/data/mybasen/python') # basen tools
#from InformerBase import * # seal py2
import string, json, re, signal, requests, base64, http.client # not httplib for py3!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import *
from droidcontroller.statekeeper import *

from droidcontroller.read_gps import * #
from droidcontroller.mybasen_send import * #

from droidcontroller.panel_seneca import *
panel = PanelSeneca(mb, mba = 3, mbi = 0, power = 0) # actual
#panel = PanelSeneca(mb, mba = 1, mbi = 0, linedict={400:900,401:901, 403:903,404:904, 406:906,407:907,409:909}, power = 0) # test


import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

requests_log = logging.getLogger("requests.packages.urllib3") # to see more
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

ts = time.time()

led = [] # lighting instances
for i in range(4): # button triggers
    led.append(StateKeeper(off_tout = 14400, on_tout = 0)) # 4 h timeout

class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''
        self.aid = 'itvilla'
        self.uid = b'itvilla' # binary!
        self.passwd = b'MxPZcbkjdFF5uEF9' # binary!
        self.path= 'tutorial/testing/sauna'
        self.url = 'https://mybasen.pilot.basen.com/_ua/'+self.aid+'/v0.1/data'

        self.values2basen = {}
        #self.bs = MyBasenSend(aid = 'itvilla', uid = b'itvilla', passwd = b'MxPZcbkjdFF5uEF9', path= 'tutorial/testing/test_async')
        self.bs = MyBasenSend(aid = 'itvilla', uid = b'itvilla', passwd = b'MxPZcbkjdFF5uEF9', path= 'tutorial/testing/sauna')
        self.channels_setup()
        
        self.ca = ControllerApp(self.app)
        self.di = None
        self.footwarning = 0
        self.chlevel = 0
        self.last_chlevel = 0
        self.panelpower = 0
        self.ledstates = [0, 0, 0, 0]
        self.fdvalue = 777
        self.ts = time.time()

        self.charge_stop_timer = None
        self.gps = ReadGps(speed = 4800) # USB
        self.loop = tornado.ioloop.IOLoop.instance() # for gps and basen_send
        
        self.gps_scheduler = tornado.ioloop.PeriodicCallback(self.gps_reader, 60000, io_loop = self.loop) # gps 60 s AND basen_send
        #self.gps_scheduler = tornado.ioloop.PeriodicCallback(self.gps_reader, 10000, io_loop = self.loop) # gps 60 s AND basen_send
        
        self.gps_scheduler.start()
        print('ControllerApp instance created')


    def channels_setup(self):
        ''' channels for mybasen '''
        channels2basen = {}
        channels2basen.update({0:['TempSauna','double',10]}) # name, type, divisor
        channels2basen.update({1:['TempBath','double',10]})
        channels2basen.update({2:['TempOutdoor','double',10]})
        channels2basen.update({3:['TempBattery','double',10]})
        channels2basen.update({4:['VoltageBatt','double',1000]})
        channels2basen.update({5:['FeetUp','double',None]})
        channels2basen.update({6:['DoorOpen','double',None]})
        channels2basen.update({7:['CoordLat','double',1]})
        channels2basen.update({8:['CoordLng','double',1]})
        channels2basen.update({9:['Light1','double',None]}) # with None do not round
        channels2basen.update({10:['Light2','double',None]}) # with None do not round
        channels2basen.update({12:['Light4','double',None]}) # with None do not round
        channels2basen.update({11:['Light3','double',None]}) # with None do not round
        self.bs.set_channels(channels2basen)


    def app(self, appinstance, attentioncode = 0):
        ''' customer-specific things, like lighting control
        # switch on panelpower if any of led strips is on
        # switch off panelpower if all led strips are off
        '''

        self.ts = time.time()
        res= 0
        footwarning = 0
        shvalue = None
        values = None
        voltage = None
        self.chlevel = 0

        di = d.get_divalues('DIW')
        do = d.get_divalues('DOW')
        if di != self.di:
            log.info('di changed: '+str(di)+', do: '+str(do)) ##

        try:
            if self.di != None and len(di) > 3: # only changes
                ledsum = 0
                for i in range(4):
                    if di[i] != self.di[i] and di[i] == 0: # change, press start
                        led[i].toggle()
                    ledstate = led[i].get_state()
                    if ledstate[0] != self.ledstates[i]:
                        log.info('light '+str(i + 1)+' new state '+str(ledstate[0])+' at '+str(int(self.ts))+' due to di['+str(i)+'] change from '+str(self.di[i])+', to '+str(di[i]))
                        self.ledstates[i] = ledstate[0]
                    
                    self.values2basen.update({9+i : ledstate[0]}) # LED states for basen
                    d.set_dovalue('LTW', i+1, ledstate[0]) # actual output service, fixed in dchannels.py 13.9.2015
                    ledsum += ledstate[0] << i
                    if ledsum > 0:
                        self.panelpower = 1
                    else:
                        self.panelpower = 0

                if self.panelpower != panel.get_power():
                    log.info('NEW panelpower '+str(self.panelpower))
                    panel.set_power(self.panelpower)
                    d.set_dovalue('PPS',1,self.panelpower)
                else:
                    log.info('no change in panelpower '+str(self.panelpower))

                if self.di != di:
                    self.di = di

            ## DATA FOR seneca S401 panel rows / via aochannels! panel update ##
            # temp temp temp temp aku jalg uks
            for i in range(7): # panel values 7 rows
                if i == 0: # sauna temp
                    aivalue = ac.get_aivalue('T1W', 1)[0] # can be None!
                elif i == 1: # bath
                    aivalue = ac.get_aivalue('T2W', 1)[0] # panel row 2
                elif i == 2: # outdoor
                    aivalue = ac.get_aivalue('T3W', 1)[0] # panel row 3
                elif i == 3: # hotwater
                    aivalue = ac.get_aivalue('T4W', 1)[0] # panel row 4, temporarely in battery box

                elif i == 4: # battery
                    batt_presence = ac.get_aivalues('BPW') # car and batt voltage presence
                    voltage = ac.get_aivalues('BTW') # panel row 5, sauna battery
                    shvalue = voltage[1] # sauna batt
                    #if voltage != None and voltage[0] != None and voltage[1] != None and voltage[0] > voltage[1] + 10 and voltage[0] > 13200: # recharging possible
                    if voltage != None and voltage[0] != None and voltage[1] != None and voltage[0] > 14300: # recharging possible # FIXME
                        self.chlevel = 1 # FIXME
                        if self.charge_stop_timer:
                            self.loop.remove_timeout(self.charge_stop_timer)

                        self.charge_stop_timer = self.loop.add_timeout(60000, self.charge_stop)

                        #if voltage[0] > voltage[1] + 1000: # low current initially
                        #    chlevel = 1
                        #elif voltage[0] < voltage[1] + 500: # directly together for faster charging ???? CHK if allowed, current and voltage
                        #    chlevel = 2

                    else:
                        self.charge_stop()  #chlevel= 0 # no car voltage present or engine stopped

                    #log.info('batt charging level '+str(chlevel)+', voltages '+str(voltage)) ##
                    if self.chlevel != self.last_chlevel:
                        log.info('NEW batt charging level '+str(self.chlevel)+', voltages '+str(voltage))
                        d.set_dovalue('BCW', 1, (self.chlevel & 1)) # via resistor
                        d.set_dovalue('BCW', 2, (self.chlevel & 2) >> 1)
                        self.last_chlevel = self.chlevel

                elif i == 5: # feet and door chk via AI1. values 3600, 3150, 2580
                    aivalue = ac.get_aivalue('A1V',1)[0] # ai1 voltage 0..4095 mV, pullup 1 k on
                    if aivalue != None:
                        if aivalue > 3700:
                            ##log.warning('feet/door line cut!')
                            fdvalue = 999
                        elif aivalue > 2400 and aivalue < 2800:
                            fdvalue = 1
                        elif aivalue > 2800 and aivalue < 3300:
                            fdvalue = 2
                        elif aivalue > 3300 and aivalue < 3700:
                            fdvalue = 3
                        elif aivalue < 1000:
                            fdvalue = 0 # ok
                        #log.info('feet/door aivalue '+str(aivalue)+', shvalue '+str(fdvalue)) ##

                        if fdvalue != 999 and fdvalue != self.fdvalue:
                            d.set_divalue('FDW',1,(fdvalue & 1))
                            d.set_divalue('FDW',2,(fdvalue & 2) >> 1)
                            log.info('NEW feet/door aivalue '+str(aivalue)+', fdvalue '+str(fdvalue))
                        self.fdvalue = fdvalue
                        shvalue = (fdvalue & 1)

                elif i == 6: # door
                    shvalue = (self.fdvalue & 2) >> 1 # door bit

                #######

                if i < 4:  # temperatures, i = 0..3
                    self.values2basen.update({i : aivalue}) ## for mybasen portal
                    if aivalue != None:
                        shvalue = int(round(aivalue / 10.0, 0))
                    else:
                        shvalue = 9999 # sensor disconnected
                else: # 4..6 here. 7,8 gpr, 9..12 lights
                    self.values2basen.update({i : shvalue})

                linereg = sorted(list(panel.get_data().keys()))[i]
                panel.send(linereg, shvalue) ## sending to panel row with correct reg address
                log.debug('sent to panel '+str((linereg, shvalue))) ##
                ac.set_aivalue('PNW', i + 1, shvalue) # to report only

            d.sync_do() # actual output writing
            self.di = di
            ##  end panel update ##

        except:
            print('main app ERROR')
            traceback.print_exc()


    def gps_reader(self):
        ''' Read GPS '''
        try:
            coord = self.gps.get_coordinates()
            if coord != None and coord[0] != None and coord[1] != None:
                ac.set_airaw('G1V',1,int(coord[0] * 1000000)) # lat
                ac.set_airaw('G2V',1,int(coord[1] * 1000000)) # lng
                self.values2basen.update({7 : coord[0]})
                self.values2basen.update({8 : coord[1]})
            else:
                log.warning('NO coordinates from GPS device, coord '+str(coord))

        except:
            print('gps ERROR')
            #traceback.print_exc()

        self.bs.basen_send(self.values2basen) ## send once a minute to basen too
        log.info('di cps '+str(round(cua.ca.spm.get_speed(),2))) # saada teenusena valja?

    def charge_stop(self):
        ''' possible battery charge stop '''
        self.chlevel = 0  # disconnnect for a while once a minute, will reconnect if needed
        if self.charge_stop_timer:
            self.loop.remove_timeout(self.charge_stop_timer)
            self.charge_stop_timer = None




############################################
cua = CustomerApp() # test like cua.ca.udp_sender() or cua.ca.app()
cua.ca.spm.start()
# test: from iomain_sauna import *; cua.values2basen.update({1:2, 0:1}); cua.bs.basen_send(cua.values2basen)

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
