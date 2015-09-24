#!/usr/bin/python

APVER='monitor 23.12.2014' # for olinuxino
# ainult monitooring ilma juhtimiseta. kasutab vajadusel ka mbus!


#################### functions ######################################################

def get_hostID(filename):
    ''' ID as mac is not reliable on olinuxino. use the mac from file to become id ! '''
    mac = None
    try:
        with open(filename) as f:
            lines = f.read().splitlines()
            mac = None
            for line in lines:
                if 'mac ' in line[0:5]:
                    mac=line[4:].replace(':','')
                    if len(mac) == 12:
                        log.info('found host id (variable mac) to become '+mac)
                    else:
                        log.error('found host id (variable mac) with WRONG length! '+mac)
    except:
        log.error('no readable file '+filename+' for host_id!')
    return mac
    
    
def comm_doall():
    ''' Handle the communication with io channels via modbus and the monitoring server  '''

    ############### conn up or down issues ################
    if udp.sk.get_state()[3] == 1: # restore now the variables from the server

        try:
            hw = hex(mb[0].read(1,257,1)[0]) # assuming it5888, mba 1!
        except:
            hw = 'n/a'

        #sendstring='AVV:HW '+hw+', APP '+APVER+'\nAVS:'
        if 'rescue' in os.path.basename(__file__):  # FIXME that should go via udpsend omitting buffer
            udp.send(['AVS',2,'AVV','HW '+hw+', APP '+APVER]) # sendstring += '2' # critical service status
        else:
            udp.send(['AVS',0,'AVV','HW '+hw+', APP '+APVER]) # sendstring += '0'
        udp.send(['TCS',1,'TCW','?']) # sendstring += '\nTCW:?\n'  # traffic counter variable to be restored
        ac.ask_counters()
        log.info('******* uniscada connectivity up, sent AVV and tried to restore counters ********')
        #udp.udpsend(sendstring)

    if udp.sk.get_state()[0] == 0: #
        if udp.sk.get_state()[1] > 300 + udp.sk.get_state()[2] * 300: # total 10 min down, cold reboot needed
            # age and neverup taken into account from udp.sk statekeeper instance
            msg = '**** going to cut power NOW (at '+str(int(time.time()))+') via 0xFEED in attempt to restore connectivity ***'
            log.warning(msg)
            udp.dump_buffer() # save unsent messages as file

            with open("/root/d4c/appd.log", "a") as logfile:
                logfile.write(msg)
            time.sleep(1)
            mb[0].write(1, 999,value = 0xFEED) # ioboard ver > 2.35 cuts power to start cold reboot (see reg 277)
            #if that does not work, appd and python main* must be stopped, to cause 5V reset without 0xFEED functionality
            try:
                p.subexec('/root/d4c/killapp',0) # to make sure power will be cut in the end
            except:
                log.warning('executing /root/d4c/killapp failed!')

    #######################
    udp.unsent() # vana jama maha puhvrist
    d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
    ac.doall() # ai koik mis vaja, loeb ja vahel raporteerib
    for mbi in range(len(mb)): # check modbus connectivity
        mberr=mb[mbi].get_errorcount()
        if mberr > 0: # errors
            print('### mb['+str(mbi)+'] problem, errorcount '+str(mberr)+' ####')
            time.sleep(2) # not to reach the errorcount 30 too fast!

    r.regular_svc() # UPW,UTW, ipV, baV, cpV. mfV are default services.
    got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees. tagastab {} saadud key:value vaartustega
    got_parse(got) # see next def
    # once again to keep up server comm despite possible extra communication
    got = udp.udpread() # loeb ainult!
    got_parse(got) # see next def
    

def got_parse(got):
    ''' check the ack or cmd from server '''
    if got != {} and got != None: # got something from monitoring server
        ac.parse_udp(got) # chk if setup or counters need to be changed
        d.parse_udp(got) # chk if setup ot toggle for di
        todo = p.parse_udp(got) # any commands or setup variables from server?

        # a few command to make sure they are executed even in case of udp_commands failure
        if todo == 'REBOOT':
            udp.udpsend('cmd:REBOOT\n')
            print('emergency stopping by main loop, stop=',stop)
            udp.dump_buffer()
            stop = 1 # kui sys.exit p sees ei moju millegiparast
            

        if todo == 'FULLREBOOT':
            print('emergency rebooting by main loop')
            udp.udpsend('cmd:FULLREBOOT\n')
            udp.dump_buffer()
            p.subexec('reboot',0) # no []
        # end making sure

        #print('main: todo',todo) # debug
        p.todo_proc(todo) # execute other possible commands

    

def app_doall():
    ''' Application part for energy metering and consumption limiting, via services if possible  '''
    global ts, ts_app, ts_mbus # , HPW, HPF
    if ts > ts_app + 20: # read mbus data from heat meter
        ts_app = ts
        
        for i in range(len(dc)):
            try:
                temp = dc[i].newcode()
                udp.send([str(i+1)+'DS', 0, str(i+1)+'DW', str(temp[0])+' '+str(temp[1])])
                temp = dc[i].get_failcode() # bitmap of sensor numbers returning 4096
                udp.send([str(i+1)+'FS', 0, str(i+1)+'FW', str((temp&8)>>3)+' '+str((temp&4) >> 2)+' '+str((temp&2) >> 1)+' '+str(temp&1)])
                
            except:
                log.warning('FAILED to chk&change 1wire delay for mba '+str(i+1))
                traceback.print_exc()
        
        if mbus_present > 0:
            try:
                m.read() # mbus data
                s.set_membervalue('HCW', 1, m.get_energy(), 'aicochannels') # cumul Wh
                s.set_membervalue('HPW', 1, m.get_power(), 'aicochannels') # 
                s.set_membervalue('HTW', 1, int(round(10.0 * m.get_temperatures()[0], 0)), 'aicochannels') # temp out
                s.set_membervalue('HTW', 2, int(round(10.0 * m.get_temperatures()[1], 0)), 'aicochannels') # temp return
                # temperature x 10!
                ts_mbus = r.uptime[0]
            except:
                log.warning('mbus related problem')
                traceback.print_exc()
            
            if m.get_errors() > 20:
                log.error('going to FULLREBOOT due to errors on Mbus!!!')
                p.subexec('reboot',0)  ########################### 
            
            if m.get_errors() > 0:
                log.warning('Mbus errorcount '+str(m.get_errors())+', going to FULLREBOOT above 20!!!')
                
            if r.uptime[0] - ts_mbus > 300: # another rebooter to be safer
                log.error('NOT going to FULLREBOOT due to errors on Mbus!!!')
                #p.subexec('reboot',0)  ############    OFF!
        else:
            log.debug('no mbus instance present!')
            



 ################  MAIN #################

import os, sys, time
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logging.getLogger('acchannels').setLevel(logging.DEBUG) # acchannels esile
#logging.getLogger('counter2power').setLevel(logging.DEBUG) # counter2power esile
#logging.getLogger('mbus').setLevel(logging.DEBUG) # mbus esile
log = logging.getLogger(__name__)

mac_ip = ['','']

# env variable HOSTNAME should be used to resolve cases with no OSTYPE information
try:
    HOSTNAME = os.environ['HOSTNAME']
    print('env var HOSTNAME is',os.environ['HOSTNAME'])
except:
    HOSTNAME='olinuxino' # 'unknown'
    print('got no env var HOSTNAME, set local var to',HOSTNAME)
    os.environ['HOSTNAME'] = HOSTNAME

try:
    OSTYPE = os.environ['OSTYPE']
    print('env var OSTYPE is',OSTYPE)
except:
    OSTYPE='archlinux'
    print('got no env var OSTYPE, set local var OSTYPE to',OSTYPE)
    os.environ['OSTYPE'] = OSTYPE

print('OSTYPE',OSTYPE, 'HOSTNAME', HOSTNAME)  # debug

from droidcontroller.udp_commands import * # sellega alusta, kaivitab ka SQlgeneral
p = Commands(OSTYPE) # setup and commands from server
r = RegularComm(interval = 120) # variables like uptime and traffic, not io channels


from droidcontroller.acchannels import * # ai and counters
from droidcontroller.dchannels import * # di, do
from droidcontroller.heatflow import * # heat flow and energy
#from droidcontroller.pid import * # pid and 3step control
from droidcontroller.delay699 import * # 1wire delay changer
dc = []
dc.append(DelayChanger(mb, 0, 1, 3, msbmin=0, msbmax=4, lsbmin=0, lsbmax=25)) # dc[0]
dc.append(DelayChanger(mb, 0, 2, 3, msbmin=0, msbmax=4, lsbmin=0, lsbmax=25)) # mbi, mba, senscount FIXME


mac = udp.get_conf('mac', 'host_id.conf') # uniscada paneb ka enda jaoks kehtima

#r.set_host_ip(ip) # ip=mac_ip[1]
udp.setID(mac) # env muutuja kaudu ehk parem?
tcp.setID(mac) #
udp.setIP('46.183.73.35') # ('195.222.15.51') # ('46.183.73.35') # mon server ip. only 195.222.15.51 has access to starman
udp.setPort(44445)




##from droidcontroller.mbus import *
#try:
#    m=Mbus() # vaikimisi port auto, autokey FTDI  # port='/dev/ttyUSB0') #
#    mbus_present = 1
#except:
#    mbus_present = 0
#    log.warning('Mbus connection NOT possible, probably no suitable USB port found!')
mbus_present = 0
    
# the following instances are subclasses of SQLgeneral.
d = Dchannels(readperiod = 0, sendperiod = 180) # di and do. immediate notification, read as often as possible.
ac = ACchannels(in_sql = 'aicochannels.sql', readperiod = 5, sendperiod = 60) # counters, power. also 32 bit ai! trigger in aichannels
#he = HeatExchange(flowrate=101/60.0, cp1=4200, tp1=20, cp2=4200, tp2=50) # 101 l/min -> l/s, vesi

# control loops
#f1=PID(P=5,I=1,D=0,min=180,max=300) # outer loop, valjund on sissepuhketemperatuur, piiratud, yhikud ddeg
#v1=ThreeStep(setpoint=0, motortime = 130, maxpulse = 10, maxerror = 2, minpulse = 2 , minerror = 0.5, runperiod = 60) # kalorifeeri ajam


s.check_setup('aicochannels')
s.check_setup('dichannels')

s.set_apver(APVER) # set version

ts = time.time() # needed for manual function testing
ts_app = 0 # time.time used for timestamping here
ts_mbus = 0 # successful mbus read, sys uptime used for timestamping!
#HPW=[]
#HFW=[]




if __name__ == '__main__':  ############################################################################
    msg = ''
    stop = 0
    if OSTYPE == 'archlinux':
        udp.led.commLED(0)
        udp.led.alarmLED(1) # because we are rebooting
    

    while stop == 0: # endless loop
        ts=time.time() # global for functions
        comm_doall()  # communication with io and server
        #app_doall() # application rules and logic, via services if possible
        # #########################################

       #time.sleep(0.1)  # main loop takt 0.1, debug jaoks suurem / jookseb kinni kui viidet pole? subprocess?
        sys.stdout.write('.') # dot without newline for main loop
        sys.stdout.flush()
    # main loop end, exit from application

