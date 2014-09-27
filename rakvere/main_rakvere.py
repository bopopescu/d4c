#!/usr/bin/python

APVER='rakvere 26.09.2014' # for olinuxino, kantselei ja kelder
# peaks iga saatmisega korraks commLED kustutama. praegu vahetub olek ainult regular vastuse puudumisel
#    aga selleks peab alati saadetud mahu tagastama, sh ac ja d report ning doall kaudu main loopi valja

import os
mac_ip = ['','']

try:
    os.environ['HOSTNAME'] = 'olinuxino' # at least sqlgeneral is using this var
    OSTYPE = os.environ['OSTYPE']
    print('env var OSTYPE is',OSTYPE)
except:
    OSTYPE='archlinux'
    print('got no env var OSTYPE, set local var OSTYPE to',OSTYPE)
    os.environ['OSTYPE'] = OSTYPE
 
from droidcontroller.udp_commands import * # sellega alusta, kaivitab ka SQlgeneral
p=Commands(OSTYPE) # setup and commands from server
r=RegularComm(interval=120) # variables like uptime and traffic, not io channels

#if os.environ['HOSTNAME'] == 'server': # test linux  
if OSTYPE == 'linux': # test linux
    #mac_ip=p.subexec('./getnetwork.sh',1).decode("utf-8").split(' ')
    mac_ip[0]='000101100000' # replace! CHANGE THIS!
    mac_ip[1] = '10.0.0.253'
    print('replaced mac_ip to',mac_ip)
elif OSTYPE == 'archlinux': # olinuxino
    mac_ip=p.subexec('/root/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
else: # techbase?
    mac_ip=p.subexec('/mnt/nand-user/d4c/getnetwork.sh',1).decode("utf-8").split(' ')
    print('unknown OSTYPE',OSTYPE,', assuming techbase!') # FIXME
    
print('mac ip',mac_ip)
mac=mac_ip[0]
ip=mac_ip[1]
r.set_host_ip(ip)

udp.setID(mac) # env muutuja kaudu ehk parem?
tcp.setID(mac) # 
udp.setIP('195.222.15.51') # ('46.183.73.35') # mon server ip. only 195.222.15.51 has access to starman
udp.setPort(44445)

from droidcontroller.acchannels import * # ai and counters
from droidcontroller.dchannels import * # di, do
#from droidcontroller.pid import * # pid and 3step control
from droidcontroller.rhco2calc import *

if OSTYPE == 'archlinux':
    from droidcontroller.gpio_led import *
    led=GPIOLED() # cpuLED, commLED, alarmLED param 0 or 1
    
# the following instances are subclasses of SQLgeneral.
d = Dchannels(readperiod = 0, sendperiod = 180) # di and do. immediate notification, read as often as possible.
ac = ACchannels(in_sql = 'aicochannels.sql', readperiod = 5, sendperiod = 30) # counters, power. also 32 bit ai! trigger in aichannels
rh = RhCoCalc(0.4, -350, 0.2, 1.1, -500, -0.75, -0.1)

s.check_setup('aicochannels')
s.check_setup('dichannels')
s.set_apver(APVER) # set version


# functions
        
def comm_doall():
    ''' Handle the communication with io channels via modbus and the monitoring server  '''
    udp.unsent() # vana jama maha puhvrist
    d.doall()  #  di koik mis vaja, loeb tihti, raporteerib muutuste korral ja aeg-ajalt asynkroonselt
    ac.doall() # ai koik mis vaja, loeb ja vahel raporteerib
    for mbi in range(len(mb)): # check modbus connectivity
        mberr=mb[mbi].get_errorcount()
        if mberr > 0: # errors
            led.alarmLED(1)
            print('### mb['+str(mbi)+'] problem, errorcount '+str(mberr)+' ####')
            time.sleep(2) # not to reach the errorcount 30 too fast!
                        
    sent=r.regular_svc(svclist = ['UPW','TCW','ip']) # uptimes, traffic. UTW,ULW are default. also forks alive processes!
    if sent != None and sent>0:
        #print('XXXX sent to server bytes',sent) # debug
        led.commLED(0) # green led off on every regular send until next response received
        #should do the same on every send! is led accessible from everywhere?
    got = udp.comm() # loeb ja saadab udp, siin 0.1 s viide sees. tagastab {} saadud key:value vaartustega
    
    if udp.read_buffer(mode=1)[0] > 30: # too many waiting svc lines in buffer
        led.alarmLED(1) # warning
    elif udp.read_buffer(mode=1)[0] == 0: # stats ok
        led.alarmLED(0) # ok
        
    if got != '' and got != None: # got something from monitoring server
        led.commLED(1)
        if got != {}:
            ac.parse_udp(got) # chk if setup or counters need to be changed
            d.parse_udp(got) # chk if setup ot toggle for di
            todo=p.parse_udp(got) # any commands or setup variables from server?
            
            # a few command to make sure they are executed even in case of udp_commands failure
            if todo == 'REBOOT':
                stop = 1 # kui sys.exit p sees ei moju millegiparast
                print('emergency stopping by main loop, stop=',stop)
            elif todo == 'FULLREBOOT':
                print('emergency rebooting by main loop')
                p.subexec('reboot',0) # no []
            elif todo.split(',')[0] == 'mbread' and len(todo.split(',')) == 5: # read any modbus register , params mbi,mba,regadd,count. return value via ERV
                print('comm_doall cmd:',todo)
                res=mb[todo.split(',')[1]].read(todo.split(',')[2],todo.split(',')[3],todo.split(',')[4]) # read value, can be tuple
                print('mbread result',res)
                sendstring += 'ERV:'+msg+'\n' # msh cannot contain colon or newline
                udp.udpsend(sendstring) # SEN
            elif todo.split(',')[0] == 'mbwrite': # write any odbus register , params mbi,mba,regadd,value. return ok via ERV
                print('comm_doall cmd:',todo)
            
            # end making sure
            # vpn start stop handled by udp_commands
            #print('main: todo',todo) # debug
            p.todo_proc(todo) # execute other possible commands
        
        
def app_doall():
    ''' Application rules and logic, via services if possible  '''
    global ts, G3W, R3S, T3W, G4V, H4V, dowant # et pysiks meeles
    
    a=0.45 # 0.41 # kordaja  niiskuse  y=ax+b
    b=-550  # -520  # nihe
    c=0.55 # temp moju

    d= 1.4 # 3.35 # co2 kordaja
    e= -750 # -650 # nihe
    f= -1 # -9.3 # temp komp
    g= -0.2 #  -1.8 # niiskuse komp
    
    try:
        # returns [sta_reg,status,val_reg,values], values are space separated
        T3W=s.get_value('T3W','aicochannels') # temp mis pysib alles
        
        H4V=s.get_value('H4V','aicochannels') # rh ai
        G4V=s.get_value('G4V','aicochannels') # co2 ai
        
        #humval=int(round(H4V[0]*a+b+c*T3W[0], 0))
        rhco2val=rh.output(T3W[0], H4V[0], G4V[0])
        humval=rhco2val[0]
        gasval=rhco2val[1]
        #gasval=int(round(G4V[0]*d+e+f*T3W[0]+g*humval, 0))
        
        res = s.set_membervalue('H3W', 1, humval, 'aicochannels')
        res += s.set_membervalue('G3W', 1, gasval, 'aicochannels')
        if res > 0: # problem
            print('s.set_membervalue problem while updating humval,gasval', humval, gasval)
        R3S=s.get_value('R3S','dichannels') # vent relay
        
        G3W=s.get_value('G3W','aicochannels') # co2 to report with lo hi
        #print('R3S, G3W, dowant', R3S, G3W, dowant) # debug
        H3W=s.get_value('H3W','aicochannels') # hum to repoprt
        print('H3W', H3W, 'R3S, G3W', R3S, G3W, 'dowant', dowant) # debug
    except:
        msg='main: app logic1 error!'
        print(msg)
        #udp.syslog(msg)
        traceback.print_exc()
        time.sleep(5)
    
    try:        
        if G3W[0] > G3W[2] or H3W[0] > H3W[2]: # start vent
            dowant = 1
        elif G3W[0] < G3W[1] and H3W[0] < H3W[1]: # stop vent
            dowant = 0
        if dowant != (R3S[0]): 
            s.setby_dimember_do('R3S',1,dowant) # do tabelisse kirjutamine
            msg='DO1 changed vent state to '+str(dowant)+' from ' +str(R3S[0])+ ' due to co2 '+str(G3W[0])+ ' and hum '+str(H3W[0])
            print(msg)
            
    except:
        msg='main: app logic2 error!'
        print(msg)
        #udp.syslog(msg)
        traceback.print_exc()
        time.sleep(5)
        
    
 # ###############  MAIN #################
ts=time.time() # needed for manual function testing
G3W=[] # keldris vaja
H3W=[] # keldri hum
R3S=[] # keldris vaja
T3W=[] # keldri temp
G4V=[] # otse ai
H4V=[] # otse ai
dowant=0 # vent 0 voi 1

if __name__ == '__main__':
    msg=''
    stop=0
    time.sleep(1)
    led.commLED(0)
    led.alarmLED(0) # because we are rebooting
    # saada apver jaj taasta valgustuse olek reboodi korral
    sendstring="AVV:"+APVER+"\nAVS:0\nHPW:?\nHFW:?"  # taastame moned seisud serverist
    udp.udpsend(sendstring)
    

    while stop == 0: # endless loop 
        ts=time.time() # global for functions
        comm_doall()  # communication with io and server
        if mac != '000101200004': # 04 on kantselei
            app_doall() # application rules and logic, via services if possible 
        
        # #########################################
        
        if len(msg)>0:
            print(msg)
            udp.syslog(msg)
            msg=''
        time.sleep(2)  # main loop takt 0.1, debug jaoks suurem 
        sys.stdout.write('.') # dot without newline for main loop
        sys.stdout.flush()        
    # main loop end, exit from application
    led.alarmLED(1)
    