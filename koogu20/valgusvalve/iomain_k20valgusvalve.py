''' highest level script for koogu20 heating & ventilation 

    lamp control testing:
    >>> cua.lamp[1].inproc('DI1W', [1,0,0,0, 0,0,0,0]); cua.ca.d.doall(); cua.ca.d.get_divalues('DO1W'); cua.lamp[1].out
'''

APVER='ioloop app valgusvalve 5.1.2016' # kasutab uut controller_app versiooni. kasuta cua.ca.d jne
## punane rs485 paar yle maja, sin paar rs485 valgusvalve. pruun paar koos +12, sin paar koos 0V akutoitelt.
import os, sys, time, traceback

#sys.path.append('/data/mybasen/python') # basen tools
#from InformerBase import * # seal py2
#import string, json, re, signal, requests, base64, http.client # not httplib for py3!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import *
#from droidcontroller.statekeeper import *
from droidcontroller.lamp import Lamp
from droidcontroller.util_n import UN # comparator here

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
    print('warning - chromalog and colorama probably not installed...')
    time.sleep(2)
    ##logging.basicConfig(format='%(name)-30s: %(asctime)s %(levelname)s %(message)s') # FIXME ei funka!
    logging.basicConfig(stream=sys.stderr, level=logging.INFO) # selles ei ole aega ega formaatimist
    
#logging.getLogger('dchannels').setLevel(logging.DEBUG) # investigate one thing, not propagated here
log = logging.getLogger(__name__)




class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp, controllerapp and so on.
            we need to control gas heating, floor valves, ventilation, blinds here
        '''

        self.ca = ControllerApp(self.app) # universal, contains ai_reader, di_reader
        self.msgbus = self.ca.msgbus # owner voimaldab unsubscribe tervele portsule korraga
        self.msgbus.subscribe('ai2di1', 'AI1W', 'valve', self.ai2di) # publish: val_reg, {'values': values, 'status': status}
        #self.msgbus.subscribe('ai2di2', 'AI2W', 'valve', self.ai2di) # publish: val_reg, {'values': values, 'status': status}
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
        # kilp 1, mba1, 2
        self.lamp.append(Lamp(self.ca.d,msgbus=self.msgbus,in_svc={'DI1W':[(1,3)]}, out_svc=['DO1W',1], name='valisvalgus', timeout=60))
        self.lamp.append(Lamp(self.ca.d,msgbus=self.msgbus,in_svc={'DI1W':[(8,3)], 'DA1W':[(1,7)]}, out_svc=['DO1W',8], name = 'kytter_valgus', timeout=60))
        self.lamp.append(Lamp(self.ca.d,msgbus=self.msgbus,in_svc={'DA1W':[(2,7)]}, out_svc=['DO2W',5], name='esikuLEDpaneel', timeout=60))
        
        #kilp4, mba 41, 42
        self.lamp.append(Lamp(self.ca.d,msgbus=self.msgbus,in_svc={'DI41W':[(4,3)]}, out_svc=['DO41W',4], name='2k_kor_lagi'))
        #self.lamp.append(Lamp(self.ca.d,msgbus=self.msgbus,in_svc={'DA1W':[(2,7)]}, out_svc=['DO2W',5], name='esikuLEDpaneel', timeout=60))
        
        log.info(str(len(self.lamp)) +' lamp instances listening to msgbus configured')
        
        


    def app(self, appinstance, attentioncode = 0): # started by a event from ca
        ''' customer-specific things, like lighting control
            appinstance is the caller name (di_reader for example.
            attentioncode can be used to control some actions.
            if di_reader calls app, then the attentioncode is 1 on change, 2 on error.
        '''
        self.ts = time.time()
        res= 0
        log.debug('>> executing app() due to '+appinstance+' attentioncode '+str(attentioncode))
        ##print('msgbus subscriptions: ', str(self.msgbus)) ##
        # kaib siit labi iga ai jarel aga midagi ei tee!
        
            
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
    
    def ai2di(self, token, subject, message): # self, token, subject, message, kuulab msgbus AI1W sonumeid
        ''' listens to the svc AI1W, ai value to binary 0 or 1, into virtual di svc of the same port '''
        log.debug('from msgbus token %s, subject %s, message %s', token, subject, str(message))
        values = message['values']
        for i in range(4): # mba1 pir sisendid
            binvalue = UN.comparator(values[i], 3440) # raw 3590 mV on movement, 3300 without
            self.ca.d.set_divalue('DA1W', i+1, binvalue) # d teeb ka publish (?) / tee allpool, kui ei tee
            if binvalue > 0:
                log.info(' == movement signal on PIR chan '+str(i)+', mba1 adi '+str(i+1))
                #cua.ca.d.set_divalue('DA1W', i+1, binvalue) # d teeb ka publish (?) / tee allpool, kui ei tee
                
        
        
        
                
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
