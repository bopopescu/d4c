''' highest level script for koogu20 heating & ventilation '''
APVER='ioloop app k20kytevent 22.11.2015' # kasutab uut controller_app versiooni. kasuta cua.ca.d jne

import os, sys, time, traceback

#sys.path.append('/data/mybasen/python') # basen tools
#from InformerBase import * # seal py2
#import string, json, re, signal, requests, base64, http.client # not httplib for py3!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import *
from droidcontroller.statekeeper import *

#from droidcontroller.read_gps import * #
from droidcontroller.mbus_watermeter import * #
#from droidcontroller.mybasen_send import * #
from droidcontroller.heating import * # includes heater, room, floor loops

import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

requests_log = logging.getLogger("requests.packages.urllib3") # to see more
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

ts = time.time()


class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp, controllerapp and so on.
            we need to control gas heating, floor valves, ventilation, blinds here
        '''

        self.ca = ControllerApp(self.app) # universal, contains ai_reader, di_reader 
        self.ts = time.time()
        
        self.loop = tornado.ioloop.IOLoop.instance() # for timing here
        
        self.watermeter = MbusWaterMeter(self.ca.ac, 'cyble_v2', 'WVCV', 'WVAV', avg_win = 3600) # vt mbus_watermeter
        self.watermeter_scheduler = tornado.ioloop.PeriodicCallback(self.watermeter_reader, 120000, io_loop = self.loop)
        self.watermeter_scheduler.start()
        
        self.gh = Heater(self.ca.d, self.ca.ac, svc_hmode='GSW', svc_Gtemp='TGW', svc_Htemp='THW', 
            svc_P='KGPW', svc_I='KGIW', svc_D='KGDW', 
            svc_pwm='PWW', svc_Gdebug='LGGW', svc_Hdebug='LGHW', svc_noint='NGIW',
            chn_gas=0, chn_onfloor=1)  # gas heater Junkers Euromaxx
        
        log.info('ControllerApp instance created and timers started')


    
    def app(self, appinstance, attentioncode = 0): # started by a event from ca
        ''' customer-specific things, like lighting control
            appinstance is the caller name (di_reader for example.
            attentioncode can be used to control some actions. 
            if di_reader calls app, then the attentioncode is 1 on change, 2 on error.
        '''
        self.ts = time.time()
        res= 0
        log.info('>> executing app() due to '+appinstance+' attentioncode '+str(attentioncode))
        if appinstance == 'ai_reader': # analogue readings refreshed
            self.gh.output() # gas heater control after every temperatures read
        
    def watermeter_reader(self):
        res = self.watermeter.read()
        if res != 0:
            log.warning('watermeter read FAILED')
        
            

############################################

cua = CustomerApp() ## test like cua.ca.udp_sender() or cua.ca.app('test') or cua.app('test',1)

log.info('use cua.method() to test methods in this main script or cua.ca.method() in the controller_app')
time.sleep(2)

if __name__ == "__main__":
    cua.ca.spm.start()
    cua.ca.di_reader()
    cua.ca.ai_reader()
    cua.watermeter_reader()
    
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
