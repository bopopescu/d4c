#!/usr/bin/python

APVER='basen sauna 07.10.2015' # for olinuxino
# get_conf kasutusse ka mac jaoks
# get_ip lisatud ip jalgimiseks, sh tun olemasolu puhul
# molemad uniscada.py sisse, mis neid vajavad (votmesonade mac ja ip kontroll!)

#####################################################


#### functions #######


def comm_doall():
    ''' Handle the communication with io channels via modbus and the monitoring server  '''

    ############### conn up or down issues ################
    global udpup
    #if udp.sk.get_state()[3] == 1: # restore now the variables from the server - kuna 2 paringut, siis jaab tous vahele
    if udp.sk.get_state()[0] == 1 and udpup == 0: # restore now the variables from the server
        udpup = 1
        try:
            hw = hex(mb[0].read(1,257,1)[0]) # assuming it5888, mba 1!
        except:
            hw = 'n/a'

        #send via buffer only!
        # use udp.send(sta_reg,status,val_reg,value) # only status is int, the rest are str

        sendstring='AVV:HW '+hw+', APP '+APVER+'\nAVS:'
        if 'rescue' in os.path.basename(__file__):
            udp.send(['AVS',2,'AVV','HW '+hw+', APP '+APVER])  
            sendstring += '2\n' # critical service status
        else:
            udp.send(['AVS',0,'AVV','HW '+hw+', APP '+APVER]) 
            sendstring += '0\n'
        udp.send(['TCS',1,'TCW','?']) # restore via buffer
        #sendstring += '\nTCW:?\n'  # traffic counter variable to be restored
        for i in range(3):
            udp.send(['H'+str(i+1)+'CS',1,'H'+str(i+1)+'CW','?']) # cumulative heat energy restoration via buffer
            #sendstring += '\nTCW:?\n'  # cumulative traffic to be restored
        ac.ask_counters()
        log.info('******* uniscada connectivity up, sent AVV and tried to restore counters and some variables ********')
        udp.udpsend(sendstring) # AVV only, the rest go via buffer

    if udp.sk.get_state()[0] == 0: #
        udpup = 0
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
            stop = 1 # kui sys.exit p sees ei moju millegiparast
            print('emergency stopping by main loop, stop=',stop)
            udp.dump_buffer()

        if todo == 'FULLREBOOT':
            print('emergency rebooting by main loop')
            udp.dump_buffer()
            p.subexec('reboot',0) # no []
        # end making sure

        #print('main: todo',todo) # debug
        p.todo_proc(todo) # execute other possible commands

    
def app_doall():  
    ''' Application rules and logic for energy metering and consumption limiting, via services if possible  '''
    global ts, ts_app, self_di, self_ledstates, self_chlevel, self_fdvalue, self_panelpower, self_ts_gps
    ts_app = time.time()
    res= 0
    footwarning = 0
    shvalue = None
    fdvalue = 999
    values = None
    voltage = None
    chlevel = 0
    
    di = d.get_divalues('DIW')
    do = d.get_divalues('DOW')
    if self_di != None and di != self_di:
        log.info('di changed: '+str(di)+', do: '+str(do)) ##

    # switch on panelpower if any of led strips is on
    # switch off panelpower if all led strips are off
    
    try:
        if di != self_di: # only changes
            ledsum = 0
            for i in range(4):
                if self_di[i] != None and di[i] != None and di[i] != self_di[i] and di[i] == 0: # change, press start
                    led[i].toggle()
                ledstate = led[i].get_state()
                if ledstate[0] != self_ledstates[i]:
                    log.info('light '+str(i + 1)+' new state '+str(ledstate[0]))
                    self_ledstates[i] = ledstate[0]
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
                
                        
        ## DATA FOR seneca S401 panel rows / via aochannels! panel update ##
        # temp temp temp temp aku jalg uks 
        for i in range(7): # panel values 7 rows
            if i == 0: # sauna temp
                aivalue = ac.get_aivalue('T1W', 1)[0] # can be None!
            elif i == 1: # bath
                aivalue = ac.get_aivalue('T2W', 1)[0] # panel row 2
            elif i == 2: # outdoor
                aivalue = ac.get_aivalue('T3W', 1)[0] # panel row 3
            ##elif i == 3: # hotwater
            ##    aivalue = ac.get_aivalue('T4W', 1)[0] # panel row 4

            elif i == 4: # battery
                batt_presence = ac.get_aivalues('BPW') # car and batt voltage presence
                voltage = ac.get_aivalues('BTW') # panel row 5, sauna battery
                shvalue = voltage[1] # sauna batt
                #if voltage != None and voltage[0] != None and voltage[1] != None and voltage[0] > voltage[1] + 10 and voltage[0] > 13200: # recharging possible
                if voltage != None and voltage[0] != None and voltage[1] != None and voltage[0] > 13300: # recharging possible
                    chlevel = 1 # FIXME
                    #if voltage[0] > voltage[1] + 1000: # low current initially
                    #    chlevel = 1
                    #elif voltage[0] < voltage[1] + 500: # directly together for faster charging ???? CHK if allowed, current and voltage
                    #    chlevel = 2
                    
                    # possible battery charge stop
                    if ts_app > self_ts_batt + 60: # move that to ioloop timers
                        self_ts_batt = ts_app
                        chlevel = 0  # disconnnect for a while once a minute, will reconnect if needed
                else:
                    chlevel= 0 # no car voltage present or engine stopped

                #log.info('batt charging level '+str(chlevel)+', voltages '+str(voltage)) ##
                if chlevel != self_chlevel:
                    log.info('NEW batt charging level '+str(chlevel)+', voltages '+str(voltage)) 
                    d.set_dovalue('BCW', 1, (chlevel & 1)) # via resistor
                    d.set_dovalue('BCW', 2, (chlevel & 2) >> 1)
                    self_chlevel = chlevel


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
                if aivalue != None:
                    shvalue = int(round(aivalue / 10.0, 0))
                else:
                    shvalue = 9999 # sensor disconnected
                
            linereg = sorted(list(panel.get_data().keys()))[i]
            panel.send(linereg, shvalue) ## sending to panel row with correct reg address
            log.debug('sent to panel '+str((linereg, shvalue))) ##
            ac.set_aivalue('PNW', i + 1, shvalue) # to report only
            #ac.set_aosvc('PNW', i + 1, shvalue) # panel row register write in aochannels
            #log.debug('PNW.'+str(i + 1)+' '+str(shvalue))

            
        d.sync_do() # actual output writing
        self_di = di
        #ac.sync_ao() # no need with panel instance in use
        #print('app panelpower '+str(panel.get_power)) ##
        ##  end panel update ##

    except:
        print('main app ERROR')
        traceback.print_exc()
    

    if gps and ts_app > self_ts_gps + 30:
        self_ts_gps = ts_app
        try:
            coord = gps.get_coordinates()
            if coord != None and coord[0] != None and coord[1] != None:
                ac.set_airaw('G1V',1,int(coord[0] * 1000000)) # lat
                ac.set_airaw('G2V',1,int(coord[1] * 1000000)) # lng
            else:
                log.warning('NO coordinates from GPS device, coord '+str(coord))
            
        except:
            print('gps ERROR')
            traceback.print_exc()
    
    #print('### main app end ###'+str(self_panelpower)) ####### app end ####
        


 ################  MAIN #################

import logging, os, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
#logging.getLogger('acchannels').setLevel(logging.DEBUG) # acchannels esile
#logging.getLogger('dchannels').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

# env variable HOSTNAME should be set before starting python
try:
    print('HOSTNAME is',os.environ['HOSTNAME'])
    # FIXME set OSTYPE
except:
    os.environ['HOSTNAME']='olinuxino' # to make sure it exists on background of npe too
    print('set HOSTNAME to '+os.environ['HOSTNAME'])

OSTYPE='archlinux'
print('OSTYPE',OSTYPE)

from droidcontroller.udp_commands import * # sellega alusta, kaivitab ka SQlgeneral
from droidcontroller.loadlimit import * # load limitation level 0..3 to be calculation

p = Commands(OSTYPE) # setup and commands from server
r = RegularComm(interval=120) # variables like uptime and traffic, not io channels

mac = udp.get_conf('mac', 'host_id.conf') # uniscada paneb ka enda jaoks kehtima
#ip = udp.get_ip() # paneb ka uniscada enda jaoks paika. initsialiseerimisel votab ka ise!

#print('mac ip', mac, ip)
# mac=mac_ip[0]
#r.set_host_ip(ip)
#print('mac, ip', mac, ip)

udp.setID(mac) # env muutuja kaudu ehk parem?
tcp.setID(mac) #
udp.setIP('46.183.73.35') # '195.222.15.51') # ('46.183.73.35') # mon server ip. only 195.222.15.51 has access to starman
udp.setPort(44445)


from droidcontroller.acchannels import *
from droidcontroller.dchannels import *

# the following instances are subclasses of SQLgeneral.
d = Dchannels(readperiod = 0, sendperiod = 120) # di and do. immediate notification, read as often as possible.
ac = ACchannels(in_sql = 'aicochannels.sql', readperiod = 5, sendperiod = 30) # counters, power. also 32 bit ai! trigger in aichannels

s.check_setup('aicochannels')
#s.check_setup('dichannels')
#s.check_setup('counters')

s.set_apver(APVER) # set version

##from droidcontroller.pic_update import *
##pic = PicUpdate(mb) # to replace ioboard fw should it be needed. use pic,update(mba, file)

from droidcontroller.read_gps import * #
gps = ReadGps(speed = 4800) # USB

from droidcontroller.panel_seneca import *
panel = PanelSeneca(mb, mba = 3, mbi = 0, power = 0) # actual. no negative!
#panel = PanelSeneca(mb, mba = 1, mbi = 0, linedict={400:-999,401:-999, 403:-999,404:-999, 406:-999,407:-999,409:-999}, power = 0) # test

####
#from droidcontroller.nagios import NagiosMessage # paralleelteated otse starmani
#nagios = NagiosMessage(mac, 'service_energy_ee', nagios_ip='62.65.192.33', nagios_port=50000)
#udp.set_copynotifier(nagios.output_and_send) # mida kasutada teadete koopia saatmiseks nagiosele. kui puudub, ei saada koopiaid.
####

ts = time.time() # needed for manual function testing
ts_app = ts
self_di = [None, None, None, None]
self_ledstates = [0, 0, 0, 0]
self_chlevel = 0
self_fdvalue = 0
self_panelpower = 0
self_ts_gps = time.time()
led = [] # lighting instances
from droidcontroller.statekeeper import *
for i in range(4): # button triggers
    led.append(StateKeeper(off_tout = 3600, on_tout = 0))
    
#from droidcontroller.statekeeper import * # vorreldes glob muutujatega kukub ise down
#hp1fail  = StateKeeper(off_tout=100) # soojuspumba 1 rike, lubab luba varujahutust
#hp2 = StateKeeper(off_tout=100) # soojuspumba 1 olek, kui up, siis ei luba varujahutust

##udp.setID(udp.get_conf('mac', 'mac.conf')) # host id

if __name__ == '__main__':
    #kontrollime energiamootjate seisusid. koik loendid automaatselt?
    msg=''
    stop=0

    while stop == 0: # endless loop
        ts = time.time() # global for functions
        comm_doall()  # communication with io and server
        app_doall() # application rules and logic, via services if possible
        #crosscheck() # check for phase consumption failures
        # #########################################

        if len(msg)>0:
            print(msg)
            udp.syslog(msg)
            msg=''
        #time.sleep(1)  # main loop takt 0.1, debug jaoks suurem
        sys.stdout.write('.') # dot without newline for main loop
        sys.stdout.flush()
    # main loop end, exit from application