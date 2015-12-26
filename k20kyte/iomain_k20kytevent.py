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
from droidcontroller.gasheater import JunkersHeater
from droidcontroller.heating import * # includes RoomTemperature, FloorTemperature

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
        self.msgbus = self.ca.msgbus
        self.msgbus.subscribe('water', 'WVCV', 'water', self.make_water_svc) # publish: val_reg, {'values': values, 'status': status}
        self.ts = time.time()
        
        self.loop = tornado.ioloop.IOLoop.instance() # for timing here
        
        self.watermeter = MbusWaterMeter(self.msgbus, 'cyble_v2', 'WVCV', 'WVAV', avg_win = 3600) # vt mbus_watermeter
        self.watermeter_scheduler = tornado.ioloop.PeriodicCallback(self.watermeter_reader, 120000, io_loop = self.loop)
        self.watermeter_scheduler.start()
        
        
        
        self.gh = JunkersHeater(self.ca.d, self.ca.ac, self.msgbus, svc_hmode='GSW', svc_Gtemp='TGW', svc_Htemp='THW', 
            svc_P='KGPW', svc_I='KGIW', svc_D='KGDW', svc_pwm='PWW', svc_Gdebug='LGGW', 
            svc_Hdebug='LGHW', svc_noint='NGIW', chn_gas=0, chn_onfloor=1)  # gas heater Junkers Euromaxx  # FIXME to msgbus
            
        self.floorperiod = 1000 # s
        self.fls = []
        # mba 2
        self.fls.append({'name':'1k_kab', 'act_svc':['T4W',4], 'set_svc':['T4W',3], 'out_svc':['HV2W',1], 'pwm_svc':['PH2W',1], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_hall1', 'act_svc':['T7W',2], 'set_svc':['T7W',1], 'out_svc':['HV2W',2], 'pwm_svc':['PH2W',2], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_kook1', 'act_svc':['T3W',4], 'set_svc':['T3W',3], 'out_svc':['HV2W',3], 'pwm_svc':['PH2W',3], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_kook2', 'act_svc':['T3W',5], 'set_svc':['T3W',3], 'out_svc':['HV2W',4], 'pwm_svc':['PH2W',4], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_hall2', 'act_svc':['T7W',3], 'set_svc':['T7W',1], 'out_svc':['HV2W',5], 'pwm_svc':['PH2W',5], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_esik', 'act_svc':['T7W',4], 'set_svc':['T7W',1], 'out_svc':['HV2W',6], 'pwm_svc':['PH2W',6], 'lolim':150, 'hilim':350})
        
        #mba 3
        self.fls.append({'name':'1k_wc', 'act_svc':['T6W',3], 'set_svc':['T6W',1], 'out_svc':['HV3W',1], 'pwm_svc':['PH3W',1], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_dush', 'act_svc':['T6W',2], 'set_svc':['T6W',1], 'out_svc':['HV3W',2], 'pwm_svc':['PH3W',2], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_talve1', 'act_svc':['T5W',4], 'set_svc':['T5W',3], 'out_svc':['HV3W',3], 'pwm_svc':['PH3W',3], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_talve2', 'act_svc':['T5W',5], 'set_svc':['T5W',3], 'out_svc':['HV3W',4], 'pwm_svc':['PH3W',4], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_elu1', 'act_svc':['T3W',6], 'set_svc':['T3W',3], 'out_svc':['HV3W',5], 'pwm_svc':['PH3W',5], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'1k_elu2', 'act_svc':['T3W',7], 'set_svc':['T3W',3], 'out_svc':['HV3W',6], 'pwm_svc':['PH3W',6], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'lk_elu3', 'act_svc':['T3W',8], 'set_svc':['T3W',3], 'out_svc':['HV3W',7], 'pwm_svc':['PH3W',7], 'lolim':150, 'hilim':350})
                
        #mba4 
        self.fls.append({'name':'floor_dusch2k', 'act_svc':['TEW',4], 'set_svc':['TEW',3], 'out_svc':['HV4W',1], 'pwm_svc':['PH4W',1], 'lolim':150, 'hilim':350})
        self.fls.append({'name':'floor_M3', 'act_svc':['TDW',4], 'set_svc':['TDW',3], 'out_svc':['HV4W',2], 'pwm_svc':['PH4W',2], 'lolim':150, 'hilim':350}) 
        self.fls.append({'name':'floor_M2', 'act_svc':['TKW',4], 'set_svc':['TKW',3], 'out_svc':['HV4W',3], 'pwm_svc':['PH4W',3], 'lolim':150, 'hilim':350}) 
        self.fls.append({'name':'floor_M1', 'act_svc':['TBW',4], 'set_svc':['TBW',3], 'out_svc':['HV4W',4], 'pwm_svc':['PH4W',4], 'lolim':150, 'hilim':350}) 
        self.fls.append({'name':'floor_gallery', 'act_svc':['TRW',4], 'set_svc':['TRW',3], 'out_svc':['HV4W',5], 'pwm_svc':['PH4W',5], 'lolim':150, 'hilim':350}) 
        
        #mba 5
        self.fls.append({'name':'2k_garde', 'act_svc':['TAW',4], 'set_svc':['TAW',3], 'out_svc':['HV5W',1], 'pwm_svc':['PH5W',1], 'lolim':150, 'hilim':350}) 
        self.fls.append({'name':'2k_vanni', 'act_svc':['T9W',4], 'set_svc':['T9W',3], 'out_svc':['HV5W',2], 'pwm_svc':['PH5W',2], 'lolim':150, 'hilim':350}) 
        self.fls.append({'name':'2k_MB2', 'act_svc':['T8W',5], 'set_svc':['T8W',3], 'out_svc':['HV5W',3], 'pwm_svc':['PH5W',3], 'lolim':150, 'hilim':350}) 
        self.fls.append({'name':'2k_MB1', 'act_svc':['T8W',4], 'set_svc':['T8W',3], 'out_svc':['HV5W',4], 'pwm_svc':['PH5W',4], 'lolim':150, 'hilim':350}) 
        
        log.info('floor heating loops configuration: '+str(self.fls)) # 22 tk kokku
        
        self.floop = []
        if len(self.fls) > 0:
            delayperphase = self.floorperiod / len(self.fls) 
            for i in range(len(self.fls)): # class FloorTemperature from heating.py 
                self.floop.append(FloorTemperature(self.msgbus, 
                act_svc = self.fls[i]['act_svc'], set_svc=self.fls[i]['set_svc'], out_svc = self.fls[i]['out_svc'], 
                name = self.fls[i]['name'], period = self.floorperiod, phasedelay = (i * delayperphase), 
                lolim = self.fls[i]['lolim'], hilim = self.fls[i]['hilim']))
            log.info(str(len(self.fls))+' floor loops created')
        
        self.airloops = []    
        
        
        
        log.info('CustomerApp instance created and ioloop timers started')


    
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
        
        if appinstance == 'ai_reader': # analogue readings refreshed
            self.gh.output() # gas heater control after every temperatures read
            bitouts = []
            pwmouts = []
            setpoints = []
            actuals = []
            for i in range(len(self.fls)): # floor loops 
                #sys.stdout.write('floor loop '+str(i)+':'+self.fls[i]['name']+', ')
                loopout = self.floop[i].output()  # find the needed floor valve state
                act = self.floop[i].pid.getvars(filter='actual') 
                set = self.floop[i].pid.getvars(filter='setpoint') 
                bit = loopout[0]
                pwm = int(10.0 * loopout[1])
                if bit != None:
                    cua.ca.d.setby_dimember_do(self.fls[i]['out_svc'][0], self.fls[i]['out_svc'][1], bit) # svc, member, value
                    bitouts.append(bit)
                    pwmouts.append(pwm)
                    cua.ca.ac.set_aivalue(self.fls[i]['pwm_svc'][0], self.fls[i]['pwm_svc'][1], pwm) ### ac.set_aivalue(svc, member, volume) ###
                    actuals.append(act) ##
                    setpoints.append(set) ##
                else:
                    log.warning('INVALID do bit value '+str(bit)+' for '+str(self.fls[i]['out_svc']))
                # the previous cannot be combined into words, may be spread over extensions
            #sys.stdout.flush()
            log.info('floor loop pwm_levels %s, valve_states %s' % (str(pwmouts), str(bitouts)))
            log.info('floor loop setpoints %s' % str(setpoints)) ##
            log.info('floor loop actuals %s' % str(actuals)) ##
            
    def watermeter_reader(self):
        res = self.watermeter.read()
        if res != 0:
            log.warning('watermeter read FAILED')
        
    def make_water_svc(self, token, subject, message): # self, token, subject, message
        ''' listens to the water volume, stores into channel / service tables ''' 
        log.info('from watermeter token %s, subject %s, message %s', token, subject, str(message))
        cua.ca.ac.set_aivalue(subject, 1, message['values'][0]) # ac.set_aivalue(svc, member, volume)
        
############################################

cua = CustomerApp() ## test like cua.ca.udp_sender() or cua.ca.app('test') or cua.app('test',1)
# methods in sqlgeneral are accessible via cua.ca.d or cua.caq.ac!
log.info('use cua.method() to test methods in this main script or cua.ca.method() in the controller_app')
time.sleep(2)

if __name__ == "__main__":
    cua.ca.spm.start()
    cua.ca.di_reader()
    cua.ca.ai_reader()
    cua.watermeter_reader()
    
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
