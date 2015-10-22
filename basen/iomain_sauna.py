APVER='ioloop app basen 18.10.2015' # miks sellega vahel udp saatmine ei hakka toole? main_sauna on parem selles osas.
# aga see on veidi kiirem, kui main_sauna

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

import os, sys, time, traceback

#sys.path.append('/data/mybasen/python') # basen tools
#from InformerBase import * # seal py2
import string, json, re, signal, requests, base64, http.client # not httplib for py3!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import *
from droidcontroller.statekeeper import *

from droidcontroller.read_gps import * #


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

self_di = [0, 0, 0, 0]
self_ledstates = [0, 0, 0, 0]
self_fdvalue = 0
self_panelpower = 0
ts = time.time()
channels2basen = {}
channels2basen.update({0:['TempSauna','double',10]}) # name, type, divisor
channels2basen.update({1:['TempBath','double',10]})
channels2basen.update({2:['TempOutdoor','double',10]})
channels2basen.update({3:['TempBattery','double',10]})
channels2basen.update({4:['VoltageBatt','double',1000]})
channels2basen.update({5:['FeetUp','double',None]})
channels2basen.update({6:['DoorOpen','double',None]})
channels2basen.update({7:['CoordLat','long',1]})
channels2basen.update({8:['CoordLng','long',1]})
channels2basen.update({9:['Light1','double',None]}) # with None do not round
channels2basen.update({10:['Light2','double',None]}) # with None do not round
channels2basen.update({11:['Light3','double',None]}) # with None do not round
channels2basen.update({12:['Light4','double',None]}) # with None do not round
values2basen = {} # id:value

led = [] # lighting instances
for i in range(4): # button triggers
    led.append(StateKeeper(off_tout = 3600, on_tout = 0))

class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''
        self.aid = 'itvilla'
        self.uid = b'itvilla' # binary!
        self.passwd = b'MxPZcbkjdFF5uEF9' # binary!
        self.path= 'tutorial/testing/sauna'
        self.url = 'https://mybasen.pilot.basen.com/_ua/'+self.aid+'/v0.1/data'

        self.ca = ControllerApp(self.app)
        self.di = None
        self.footwarning = 0
        self.chlevel = 0
        self.last_chlevel = 0
        self.panelpower = 0
        self.ledstates = [0, 0, 0, 0]
        self.fdvalue = 777
        self.charge_stop_timer = None
        self.gps = ReadGps(speed = 4800) # USB
        self.loop = tornado.ioloop.IOLoop.instance() # for gps and basen_send
        self.gps_scheduler = tornado.ioloop.PeriodicCallback(self.gps_reader, 60000, io_loop = self.loop) # gps 60 s AND basen_send
        self.gps_scheduler.start()
        print('ControllerApp instance created')


    def app(self, appinstance):
        ''' customer-specific things, like lighting control
        # switch on panelpower if any of led strips is on
        # switch off panelpower if all led strips are off
        '''

        global ts, self_di, self_ledstates, self_fdvalue, self_panelpower, self_ts_gps, channels2basen, values2basen
        ts = time.time()
        res= 0
        footwarning = 0
        shvalue = None
        values = None
        voltage = None
        self.chlevel = 0

        di = d.get_divalues('DIW')
        do = d.get_divalues('DOW')
        if di != self_di:
            log.info('di changed: '+str(di)+', do: '+str(do)) ##

        try:
            if self_di != None and di != self_di: # only changes
                ledsum = 0
                for i in range(4):
                    if di[i] != self_di[i] and di[i] == 0: # change, press start
                        led[i].toggle()
                    ledstate = led[i].get_state()
                    if ledstate[0] != self_ledstates[i]:
                        log.info('light '+str(i + 1)+' new state '+str(ledstate[0]))
                        self_ledstates[i] = ledstate[0]
                        values2basen.update({9+i : ledstate[0]}) # for basen
                    d.set_dovalue('LTW', i+1, ledstate[0]) # actual output service, fixed in dchannels.py 13.9.2015
                    ledsum += ledstate[0] << i
                    if ledsum > 0:
                        panelpower = 1
                    else:
                        panelpower = 0

                if panelpower != panel.get_power():
                    log.info('NEW panelpower '+str(panelpower))
                    panel.set_power(panelpower)
                    d.set_dovalue('PPS',1,panelpower)
                else:
                    log.info('no change in panelpower '+str(panelpower))

                self_di = di

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

                        if fdvalue != 999 and fdvalue != self_fdvalue:
                            d.set_divalue('FDW',1,(fdvalue & 1))
                            d.set_divalue('FDW',2,(fdvalue & 2) >> 1)
                            log.info('NEW feet/door aivalue '+str(aivalue)+', fdvalue '+str(fdvalue))
                        self_fdvalue = fdvalue
                        shvalue = (fdvalue & 1)

                elif i == 6: # door
                    shvalue = (self_fdvalue & 2) >> 1 # door bit in self_dvalue

                #######

                if i < 4:  # temperatures, i = 0..3
                    values2basen.update({i : aivalue}) ## for mybasen portal
                    if aivalue != None:
                        shvalue = int(round(aivalue / 10.0, 0))
                    else:
                        shvalue = 9999 # sensor disconnected
                else: # 4..6 here. 7,8 gpr, 9..12 lights
                    values2basen.update({i : shvalue})

                linereg = sorted(list(panel.get_data().keys()))[i]
                panel.send(linereg, shvalue) ## sending to panel row with correct reg address
                log.debug('sent to panel '+str((linereg, shvalue))) ##
                ac.set_aivalue('PNW', i + 1, shvalue) # to report only

            d.sync_do() # actual output writing
            self_di = di
            ##  end panel update ##

        except:
            print('main app ERROR')
            traceback.print_exc()


    def gps_reader(self):
        ''' Read GPS '''
        global values2basen
        try:
            coord = self.gps.get_coordinates()
            if coord != None and coord[0] != None and coord[1] != None:
                ac.set_airaw('G1V',1,int(coord[0] * 1000000)) # lat
                ac.set_airaw('G2V',1,int(coord[1] * 1000000)) # lng
                values2basen.update({7 : coord[0]})
                values2basen.update({8 : coord[1]})
            else:
                log.warning('NO coordinates from GPS device, coord '+str(coord))

        except:
            print('gps ERROR')
            traceback.print_exc()
        self.basen_send() ## send once a minute to basen too

    def mybasen_rows(self):
        ''' Create datta rows for mybasen '''
        global values2basen, channels2basen
        self.rows = []
        for key in values2basen: # some channels may be without value in the beginning. add time?
            # show chan, type, value
            if channels2basen[key][2] != None:
                value = values2basen[key] / channels2basen[key][2]
            else:
                value = int(values2basen[key])
            #log.info('4basen '+str(channels2basen[key][0:2])+' '+str(value))
            row = "{"
            row += "\"channel\":\"" + str(channels2basen[key][0]) + "\","
            row += "\"" + str(channels2basen[key][1]) + "\":" + str(value) # + ","
            #row += "\"comment\":\"" + str(self.comment) + "\","
            #row += "\"unit\":\"" + str(self.unit) + "\""
            row += "}"
            log.info(row)
            self.rows.append(row)

    def createhttpheaders(self):
        '''create basic auth headers'''
        authstr = 'aXR2aWxsYTpNeFBaY2JramRGRjV1RUY5' # in base64  FIXME
            #"Basic %s" % (
            #base64.b64encode("%s:%s" % (
            #        self.uid, self.passwd)),)
        self.httpheaders = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + authstr
            }
        log.info('headers: '+str(self.httpheaders))


    def domessage(self):
        ''' Create json message for the given subpath and uid+password '''
        # [{"dstore":{"path":"tutorial/testing/unit1","rows":[{"channels":[{"channel":"temp","double":23.3},{"channel":"weather","string":"Balmy"}]}]}}] # naide
        # [{"dstore":{"path":"tutorial/testing/sauna","rows":[{"channels":[{"channel":"TempSauna","double":0.1},{"channel":"TempBath","double":0.2}]}]}}] # tekib ok
        msg = '[{\"dstore\":{\"path\":'
        msg += '\"' + self.path + '\",'
        msg += '\"rows\":[{"channels":['
        for row in self.rows:
            msg += row
            msg += ","
        msg = msg.rstrip(",")
        msg += ']}]}}]'  # close
        log.debug('msg: '+str(msg))
        return msg

    def mybasen_send(self, message):
        '''Send the message over https POST'''
        self.createhttpheaders()
        try:
            #r = requests.post(self.url, data=message, headers=self.httpheaders) # NOT SUPPORTED!
            r = requests.put(self.url, data=message, headers=self.httpheaders) # returns status code
            log.info('response: '+str(r.content))
        except:
            logging.error("https connection to mybasen failed")
            traceback.print_exc()
            return False

        #if r != 200:
        #    logging.error("https connection response not ok "+str(r))
        #    return False
        return True



    def charge_stop(self):
        ''' possible battery charge stop '''
        self.chlevel = 0  # disconnnect for a while once a minute, will reconnect if needed
        if self.charge_stop_timer:
            self.loop.remove_timeout(self.charge_stop_timer)
            self.charge_stop_timer = None


    def basen_send(self):
        ''' the whole sending process with ioloop timer '''
        global values2basen
        if len(values2basen) > 0: # initially empty
            self.mybasen_rows()
            self.mybasen_send(self.domessage())



############################################
cua = CustomerApp() # test like cua.ca.udp_sender() or cua.ca.app()
# test: from iomain_sauna  import *; values2basen.update({1:2, 0:1}); cua.mybasen_rows(); mess=cua.domessage(); cua.mybasen_send(mess)
if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
