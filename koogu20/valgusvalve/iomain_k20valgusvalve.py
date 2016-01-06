''' highest level script for koogu20 heating & ventilation '''
APVER='ioloop app valgusvalve 5.1.2016' # kasutab uut controller_app versiooni. kasuta cua.ca.d jne

import os, sys, time, traceback

#sys.path.append('/data/mybasen/python') # basen tools
#from InformerBase import * # seal py2
#import string, json, re, signal, requests, base64, http.client # not httplib for py3!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import *
#from droidcontroller.statekeeper import *
from droidcontroller.lamp import Lamp

#from droidcontroller.read_gps import * #
#from droidcontroller.mbus_watermeter import * #
#from droidcontroller.mybasen_send import * #
#from droidcontroller.gasheater import JunkersHeater
#from droidcontroller.heating import * # includes RoomTemperature, FloorTemperature
from droidcontroller.gcal import Gcal # setpoint shifting

import logging
try:
    import chromalog # colored
    chromalog.basicConfig(level=logging.INFO, format='%(name)-30s: %(asctime)s %(levelname)s %(message)s')
except ImportError:
    logging.basicConfig(format='%(name)-30s: %(asctime)s %(levelname)s %(message)s') # 30 on laius

logging.getLogger('heating').setLevel(logging.DEBUG) # investigate one thing, not propagated here
log = logging.getLogger(__name__)




class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp, controllerapp and so on.
            we need to control gas heating, floor valves, ventilation, blinds here
        '''

        self.ca = ControllerApp(self.app) # universal, contains ai_reader, di_reader
        self.msgbus = self.ca.msgbus # owner voimaldab unsubscribe tervele portsule korraga
        #self.msgbus.subscribe('water', 'WVCV', 'water', self.make_water_svc) # publish: val_reg, {'values': values, 'status': status}
        self.ts = time.time()

        self.loop = tornado.ioloop.IOLoop.instance() # for timing here

        self.gcal = Gcal('010000000012') # Gcal(self.ca.udp.getID())
        #self.gcal_scheduler = tornado.ioloop.PeriodicCallback(self.gcal.read_async, 300000, io_loop = self.loop) # every 30 minutes (3 for tst) # FIXME
        #self.gcal_scheduler.start()
        
        #self.gcal2tempset_scheduler = tornado.ioloop.PeriodicCallback(self.gcal2tempset, 60000, io_loop = self.loop) # every 3 minutes (1 for test)
        #self.gcal2tempset_scheduler.start()
        

        '''
           in_svc = {svc:[(member,mtype), ], } # mtype 1 invbyup, 2 invbydn, 3 invbyboth, 
                                                       5 upbyup, 6 upbydn, 7 upbyboth
                                                       9 followhi, 10 followlo, 11 followboth
        '''
        self.lamp = [] # lomi, hilim are the pwm pulse length range in seconds (slow pwm)
        # mba1
        self.lamp.append(Lamp(in_svc={'DI1W':[(1,3)]}, out_svc=['DO1W',1], name = 'valisvalgus', timeout = 60, out = 0))
        
        self.lamp.append(Lamp(in_svc={'DI1W':[(8,3)], 'DA1W':[(1,7)]}, out_svc=['DO1W',8], name = 'kytteruumi_valgus', timeout = None, out = 0))
        
        self.lamp.append(Lamp(in_svc={'DA1W':[(2,7)]}, out_svc=['DO2W',5], name = 'esikuLEDpaneel', timeout = 60, out = 0))
        
        
        log.info(str(len(self.lamp)) +' lamp instances configured')
        
        


    def app(self, appinstance, attentioncode = 0): # started by a event from ca
        ''' customer-specific things, like lighting control
            appinstance is the caller name (di_reader for example.
            attentioncode can be used to control some actions.
            if di_reader calls app, then the attentioncode is 1 on change, 2 on error.
        '''
        self.ts = time.time()
        res= 0
        log.info('>> executing app() due to '+appinstance+' attentioncode '+str(attentioncode))
        ##print('msgbus subscriptions: ', str(self.msgbus)) ##

        #if appinstance == 'ai_reader': # analogue readings refreshed
        #    pass
            
            
            
            
    def gcal_sync(self): # use async() instead
        res = self.gcal.sync() # cal_id is host_id
        if res == 0:
            log.info('gcal synced')
        else:
            log.info('gcal sync FAILED!')

    #def gcal_async(self):
    #    res = self.gcal.async() # cal_id is host_id
    #    if res != None:
    #       log.info('gcal (a)synced, res '+str(res))
        
                
############################################

cua = CustomerApp() ## test like cua.ca.udp_sender() or cua.ca.app('test') or cua.app('test',1)
# methods in sqlgeneral are accessible via cua.ca.d or cua.caq.ac!
log.info('use cua.method() to test methods in this main script or cua.ca.method() in the controller_app')
time.sleep(2)

if __name__ == "__main__":
    cua.ca.spm.start()
    cua.ca.di_reader()
    cua.ca.ai_reader()
        
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
