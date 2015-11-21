''' highest level script for koogu20 heating & ventilation '''
APVER='ioloop app k20kytevent 15.11.2015'


import os, sys, time, traceback

#sys.path.append('/data/mybasen/python') # basen tools
#from InformerBase import * # seal py2
import string, json, re, signal, requests, base64, http.client # not httplib for py3!

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import *
from droidcontroller.statekeeper import *

#from droidcontroller.read_gps import * #
from droidcontroller.mbus import * #
#from droidcontroller.mybasen_send import * #
from droidcontroller.it5888pwm import * # pwm to io modules
from droidcontroller.pid import * # pid loops


import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
#logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

requests_log = logging.getLogger("requests.packages.urllib3") # to see more
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

ts = time.time()

try:
    
    
    pwm_present = True
except:
    pwm_present = False
    log.warning('pwm instances creation failed!')
    traceback.print_exc()
    
    
    #led = [] # lighting instances
#for i in range(4): # button triggers
#    led.append(StateKeeper(off_tout = 14400, on_tout = 0)) # 4 h timeout

class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''

        self.ca = ControllerApp(self.app)
        #self.di = None
        self.ts = time.time()
        
        self.loop = tornado.ioloop.IOLoop.instance() # for timing here
        self.mbus = Mbus(model='cyble_v2') # water meter
        self.mbus_scheduler = tornado.ioloop.PeriodicCallback(self.mbus_reader, 120000, io_loop = self.loop)
        
        self.pwm_gas = []
        self.pwm_gas.append(IT5888pwm(mb, mbi = 0, mba = 1, name='hot water pwm control', period = 1000, bits = [13])) # do6, nupupinge regul
        self.pwm_gas.append(IT5888pwm(mb, mbi = 0, mba = 1, name='floor_onTemp pwm control', period = 1000, bits = [14])) # do7, termostaadi kyte
        
        self.pid_gas = []
        self.pid_gas.append(PID(P=0.5, I=0.05, D=0, min=5, max=995, name = 'gasheater watertemp pwm setpoint'))
        self.pid_gas.append(PID(P=0.5, I=0.05, D=0, min=5, max=995, name = 'flooron watertemp pwm setpoint'))
        
        self.TGW = [None, None, 380, None] # initial gas hot setpoint in [2] in ddegC
        self.THW = [None, None, 330, None] # initial floor_on setpoint in [2] in ddegC
        
        log.info('ControllerApp instance created')


    def mbus_reader(self):
        ''' Reads and returns water meter cumulative value in litres '''
        try:
            self.mbus.read()
            volume = self.mbus.get_volume()
            log.info('got value from water meter: '+str(volume))
            ac.set_aivalue('WVCV', 1, self.val2int(volume)) # to report only, in L
            #return volume 
        except:
            log.warning('mbus water meter reading or aicochannels register writing FAILED!')
            traceback.print_exc()
            #return None
    
    def app(self, appinstance, attentioncode = 0):
        ''' customer-specific things, like lighting control
            appinstance is the caller name (di_reader for example.
            attentioncode can be used to control some actions. 
            if di_reader calls app, then the attentioncode is 1 on change, 2 on error.
        '''

        self.ts = time.time()
        res= 0
        log.info('executing app() due to '+appinstance+' attentioncode '+str(attentioncode))
        if appinstance == 'ai_reader': # analogue readings refreshed
            self.gas_heater()
        
        
        
        #di = d.get_divalues('DIW')
        #do = d.get_divalues('DOW')
        #if di != self.di:
        #    log.info('di changed: '+str(di)+', do: '+str(do)) ##

        #for i in range(3): # variables from server
        #    udp.send(['H'+str(i+1)+'CS',1,'H'+str(i+1)+'CW','?']) # cumulative heat energy restoration via buffer

        
    def val2int(self, value, coeff = 1):
        ''' Multiply with coeff, return rounded integer '''
        if value and coeff:
            return int(round(coeff * value, 0))
        else:
            log.warning('INVALID parameters! value or coeff None?')
            return None
            
    
    def gas_heater(self):
        ''' CONTROLS HEATING WATER TEMPERATURE FROM GAS HEATER AND MIX VALVE TO FLOOR '''
        try:
            # self.TGW, self.THW not used so far
            TGW = ac.get_aivalues('TGW') # water from gasheater - actual on, actual ret, setpoint, hilim
            THW = ac.get_aivalues('THW') # water to floors -  actual on, actual ret, setpoint, hilim
            KGPW = ac.get_aivalues('KGPW') # kP for loops G, H
            KGIW = ac.get_aivalues('KGIW') # kI for loops G, H
            KGDW = ac.get_aivalues('KGDW') # kD for loops G, H
            
            pwm_values = [ self.val2int(self.pid_gas[0].output(TGW[2],TGW[0])), self.val2int(self.pid_gas[1].output(THW[2],THW[0])) ]
            self.pwm_gas[0].set_value(13, pwm_values[0]) # pwm to heater knob, do bit 13
            self.pwm_gas[1].set_value(14, pwm_values[1]) # pwm to 3way valve, do bit 14
            
            tempvarsG = self.pid_gas[0].getvars() # dict
            tempvarsH = self.pid_gas[1].getvars() # dict
            ''' 
            {'Kp' : self.Kp, \
            'Ki' : self.Ki, \
            'Kd' : self.Kd, \
            'outMin' : self.outMin, \
            'outMax' : self.outMax, \
            'outP' : self.Cp, \
            'outI' : self.Ki * self.Ci, \
            'outD' : self.Kd * self.Cd, \
            'setpoint' : self.setPoint, \
            'onlimit' : self.onLimit, \
            'error' : self.error, \
            'actual' : self.actual, \
            'out' : self.out, \
            'extnoint' : self.extnoint, \
            'name': self.name }
            '''
            #print('tempvarsG',tempvarsG) # debug
            #print('tempvarsH',tempvarsH) # debug
            
            ac.set_aivalues('PWW', values = pwm_values)
            ac.set_aivalues('LGGW', values=[self.val2int(tempvarsG[error],10), self.val2int(tempvarsG['outP'],10), self.val2int(tempvarsG['outI'],10), self.val2int(tempvarsG['outD'],10) ]) # out comp x 10 for loop 0
            ac.set_aivalues('LGHW', values=[self.val2int(tempvarsG[error],10), self.val2int(tempvarsH['outP'],10), self.val2int(tempvarsH['outI'],10), self.val2int(tempvarsH['outD'],10) ]) # PID comp for loop 1
            ac.set_aivalues('NGIW', values=[tempvarsG['extnoint'], tempvarsH['extnoint'] ]) # ext int stop
            
            if self.val2int(tempvarsG['outMax']) != TGW[3]:
                self.pid_gas[0].setMax(TGW[3])
                log.warning('pid_gas[0] hilim changed to '+str(TGW[3]))
            if self.val2int(tempvarsG['Kp'],10) != KGPW[0]:
                self.pid_gas[0].setKp(KGPW[0] / 10.0)
                log.warning('pid_gas[0] kP changed!')
            if self.val2int(tempvarsG['Ki'],1000) != KGIW[0]:
                self.pid_gas[0].setKi(KGIW[0] / 1000.0)
                log.warning('pid_gas[0] kI changed!')
            if self.val2int(tempvarsG['Kd']) != KGDW[0]:
                self.pid_gas[0].setKd(KGDW[0])
                log.warning('pid_gas[0] kD changed!')
                
            if self.val2int(tempvarsH['outMax']) != THW[3]:
                self.pid_gas[1].setMax(THW[3])
                log.warning('pid_gas[1] hilim changed to '+str(THW[3]))
            if self.val2int(tempvarsH['Kp'], 10) != KGPW[1]:
                self.pid_gas[1].setKp(KGPW[1] / 10.0)
                log.warning('pid_gas[1] kP changed!')
            if self.val2int(tempvarsH['Ki'], 1000) != KGIW[1]:
                self.pid_gas[1].setKi(KGIW[1] / 1000.0)
                log.warning('pid_gas[1] kI changed!')
            if self.val2int(tempvarsH['Kd']) != KGDW[1]:
                self.pid_gas[1].setKd(KGDW[1])
                log.warning('pid_gas[1] kD changed!')
            

            log.info('gas_heater done, new pwm values '+str(pwm_values))
        except:
            log.warning('gasheater control PROBLEM')
            traceback.print_exc()
        
        

############################################
cua = CustomerApp() # test like cua.ca.udp_sender() or cua.ca.app('test') or cua.app('test',1)
cua.ca.spm.start()
cua.ca.di_reader()
cua.ca.ai_reader()
cua.mbus_reader()
log.info('use cua.method() to test methods in this main script or cua.ca.method() in the controller_app')
time.sleep(2)

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
