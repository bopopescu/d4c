#!/usr/bin/python

APVER='koskla2 28.05.2015' # for olinuxino
# get_conf kasutusse ka mac jaoks
# get_ip lisatud ip jalgimiseks, sh tun olemasolu puhul
# molemad uniscada.py sisse, mis neid vajavad (votmesonade mac ja ip kontroll!)

#####################################################


#### functions #######


def comm_doall():
    ''' Handle the communication with io channels via modbus and the monitoring server  '''

    ############### conn up or down issues ################
    if udp.sk.get_state()[3] == 1: # restore now the variables from the server

        try:
            hw = hex(mb[0].read(1,257,1)[0]) # assuming it5888, mba 1!
        except:
            hw = 'n/a'

        #send via buffer only!
        # use udp.send(sta_reg,status,val_reg,value) # only status is int, the rest are str

        #sendstring='AVV:HW '+hw+', APP '+APVER+'\nAVS:'
        if 'rescue' in os.path.basename(__file__):
            udp.send(['AVS',2,'AVV','HW '+hw+', APP '+APVER]) # sendstring += '2' # critical service status
        else:
            udp.send(['AVS',0,'AVV','HW '+hw+', APP '+APVER]) # sendstring += '0'
        udp.send(['TCS',1,'TCW','?']) # sendstring += '\nTCW:?\n'  # traffic counter variable to be restored
        for i in range(3):
            udp.send(['H'+str(i+1)+'CS',1,'H'+str(i+1)+'CW','?']) # sendstring += '\nTCW:?\n'  # cumulative energies to be restored
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
    global ts, ts_app, el_energylast, pump_old, flowperiod
    pump = [0, 0, 0]  # temporary list
    ##ts = time.time() # ajutine, testimiseks aega vaja
    flowrate = 0
    if ts < ts_app + 3: # not too often... 2 seconds min interval
        #log.info('ts',ts,'ts_app',ts_app)
        return 5

    # temperatuurid 2 anduri alusel
    if ac.get_aivalue('T0W', 2)[0] != None and ac.get_aivalue('T0W', 3)[0] != None:
        avgtemp = (ac.get_aivalue('T0W', 2)[0] + ac.get_aivalue('T0W', 3)[0]) / 2
        ac.set_aivalue('T0W', 1, int(round(avgtemp,0))) # ddegC

    di_state = s.get_value('D1W','dichannels')[0:3] # didebug svc, first 3 inputs are water meters w pulse output
    pump = s.get_value('D1W','dichannels')[3:6] # didebug svc, next 3 inputs are pumps on the same tube with previous water meters
    metercoeff = [10, 10, 10] # litres per pulse
    flowfixed = [1.67, 1.28, 0.172] # l/s
    
    msg = 'pump '+str(pump)+', di_state '+str(di_state)+', metercoeff '+str(metercoeff)+', flowperiod '+str(flowperiod)
    log.info(msg) ##
    print(msg) ##
    for i in range(3):
        log.info('app_doall starting i '+str(i)) ###
        try:
            ac.set_airaw('F'+str(5+i)+'V', 1, int(1000 * flowfixed[i] * pump[i])) ## esialgu fixed alusel ###
            
            flowrate2 = fr[i].output(pump[i], di_state[i]) # fr alusel
            log.info('app_doall i '+str(i)+', flowrate2 fr '+str(flowrate2)) ### 
            if flowrate2 != None:
                ac.set_airaw('PFW', i+1, int(1000 * flowrate2)) # fr alusel arvutatud, yks front
            else:
                ac.set_airaw('PFW', i+1, 0) # asendame nulliga
                
            flowperiod[i] = pp[i].output(pump[i], di_state[i]) # pumba too avastada di4..di6 abil.
            #if flowperiod[i] != None and flowperiod[i] > 0:
            #    flowrate = pump[i] * 1.0 * metercoeff[i] / flowperiod[i] # l/s
            #    
            #    #log.info('app_doall i '+str(i)+', flowrate pp '+str(flowrate)+', flowrate2 fr '+str(flowrate2)) ### 
            #    if flowrate > 0:
            #        pass #ac.set_aivalue('F'+str(5+i)+'V',1,str(int(1000 * flowrate))) # ka seisu ajal, ml/s
            #        
            #        ##he[i].set_flowrate(flowrate) # flow rate l/s actual update ###### esialgu fixed, vt allpool
            #        
            #    else:
            #        log.warning('illegal flowrate result '+str(flowrate))

            if he[i]:
                he[i].set_flowrate(flowfixed[i]) ## ajutine  = 5 imp 5 min jooksul kui 10 imp/l, 100 l /min. lyhikesed tootsyklid..
                if i == 0:
                    Ton = s.get_value('T51W','aicochannels')[0]
                    Tret = s.get_value('T51W','aicochannels')[1]
                    log.info('i '+str(i)+' Ton '+str(Ton)+', Tret '+str(Tret)+', pump '+str(pump[i]))
                    hrout = he[i].output(pump[i], Ton/10.0, Tret/10.0) # params di_pump, Ton, Tret; returns tuple of W, J, s
                    log.info('i '+str(i)+', Tdiff '+str(int(Ton-Tret)/10)+', di_pump '+str(pump[i])+', he.output '+str(hrout))
                    hrpwr = hrout[0]
                    if hrpwr == None or pump[i] == 0: # he.output is sometimes >0 during di_pump == 1???
                        hrpwr = 0
                    if ac.set_airaw('H1PW', 1, int(hrpwr)) != 0: # instant heat pump POWER W into svc
                        log.warning('PROBLEM with raw setting for HP1W!') 
                    
                elif i == 1:
                    Ton = s.get_value('T61W','aicochannels')[0]
                    Tret = s.get_value('T61W','aicochannels')[1]
                    log.info('i '+str(i)+' Ton '+str(Ton)+', Tret '+str(Tret)+', pump '+str(pump[i]))
                    hrout = he[i].output(pump[i], Ton/10.0, Tret/10.0) # params di_pump, Ton, Tret; returns tuple of W, J, s
                    hrpwr = hrout[0]
                    log.info('i '+str(i)+', Tdiff '+str((Ton-Tret)/10)+', di_pump '+str(pump[i])+', he.output '+str(hrout))
                    if hrpwr == None or pump[i] == 0:
                        hrpwr = 0
                    if ac.set_airaw('H2PW', 1, int(hrpwr)) != 0: # instant heat pump POWER W
                        log.warning('PROBLEM with raw setting for HP2W!') 
                elif i == 2:
                    Ton = s.get_value('T62W','aicochannels')[1]
                    # Tret = s.get_value('T62W','aicochannels')[2] # annab Ton vaartuse vahel??? ka multi graafik siuke... kui 4096?
                    Tret = s.get_value('T63V','aicochannels')[0] # see annab none asemel ilusti eelmise value
                    log.info('i '+str(i)+' Ton '+str(Ton)+', Tret '+str(Tret)+', pump '+str(pump[i]))
                    hrout = he[i].output(pump[i], Ton/10.0, Tret/10.0) # solar to SPV
                    hrpwr = hrout[0]
                    log.info('i '+str(i)+', Tdiff '+str((Ton-Tret)/10)+', di_pump '+str(pump[i])+', he.output '+str(hrout))
                    if hrpwr == None or pump[i] == 0:
                        hrpwr  = 0
                    if ac.set_airaw('SPV', 1, int(hrpwr)) != 0: # instant heat solar power
                        log.warning('PROBLEM with raw setting for SPV!') 
                else:
                    log.warning('app_doall() invalid i '+srt(i))
                
                log.info('app_doall i '+str(i)+', Ton '+str(Ton/10)+', Tret '+str(Tret/10)+', hrout[0] '+str(hrout[0]))
                
                #cumulative energies possible recovery from server
                energy = hrout[1] / 3600.0 # Ws (J) into Wh
                posenergy = hrout[3] / 3600.0 # Ws (J) into Wh
                negenergy = hrout[4] / 3600.0 # Ws (J) into Wh
                
                #voimalikud kumul energia taastamised
                cumheat = ac.get_aivalues('H'+str(i+1)+'CW') # [] of member values
                if cumheat[0] != None and cumheat[0] > energy:
                    he[i].set_energy(cumheat[0]); energy = cumheat[0] # kas liita vahepeale kogunenule?
                    he[i].set_energypos(cumheat[3]); posenergy = cumheat[3] # kas liita vahepeale kogunenule?
                    he[i].set_energyneg(cumheat[4]); negenergy = cumheat[4] # kas liita vahepeale kogunenule?
                
                ac.set_aivalues('H'+str(i+1)+'CW', [int(round(energy, 0)), int(round(posenergy, 0)), int(round(negenergy, 0))]) # Wh 
                log.info('cumulative heat energy Wh for i '+str(i)+': '+str(int(energy))+' pos '+str(int(posenergy))+' neg '+str(int(negenergy)))

                if pump[i] != pump_old[i]: # state change. i 0, 1 jaoks cop # liiga harva! parigu viimast pidevalt.
                    if pump[i] == 0: # heat pump just stopped, calc COP!
                        log.info('heat pump '+str(i+1)+' stopped, NEW COP present at '+str(ts)) # pump3 solar
                        
                    ## COP & energy calculation 
                    lastenergy = he[i].get_energylast() / 3600.0 # Ws (J) into Wh
                    el_energy = ac.get_aivalue('E'+str(i+1)+'CV', 1)[0] # cumulative el energy Wh
                    # detect the chANGE IN HEAT PUMP STATUS, store el_energy value
                    el_delta = el_energy - el_energylast[i] # kWh increment
                    el_energylast[i] = el_energy # keep in global variable until next hp stop
                    
                    if i < 2: # cop calc here
                        log.info('COP calc based on Wh el_delta '+str(el_delta)+' and lastenergy '+str(lastenergy))
                        if el_delta > 0 and (lastenergy /1000 > el_delta / 2) and (lastenergy /1000 < 10 * el_delta): # avoid division with zero and weird results
                            ac.set_airaw('CP'+str(i+1)+'V', 1, int(round((lastenergy / 100.0) / el_delta, 2))) # calculated for last cycle cop, x10
                            log.info('last heat pump '+str(i+1)+' COP '+str(round((lastenergy / 1000) / el_delta, 2))+' ('+str(lastenergy)+' / '+str(el_delta)+')')
                        else:
                            log.warning('skipped COP calc for pump '+str(i+1)+' due to heat / el '+str(lastenergy)+' / '+str(el_delta))
                            # something to restore to avoid cop loss after restart?
            
            else:
                log.warning('NO he['+str(i)+'] instance!')

        except:
            log.warning('heatflow/power calculation failed')
            traceback.print_exc()
    pump_old = pump # []
    ts_app = ts
    return 0

def crosscheck(): # FIXME: should be autoadjustable to the number of counter state channels RxyV
    ''' Report failure states (via dichannels) depending on other states (from counters for example) '''
    pass


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
l = LoadLimit(currentlevel=3, maxlevel=3, \
            leveldelay=30, \
          currentdelay=10, \
              lo_limit=180000, \
              hi_limit=200000, phasecount=3)
# use l.set_lo_limit(value_mA) to set another limit

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

from droidcontroller.pic_update import *
##pic = PicUpdate(mb) # to replace ioboard fw should it be needed. use pic,update(mba, file)

from droidcontroller.heatflow import * # heat flow and energy
he = []
pp = []
fr = []
for i in range(3):
    he.append(HeatExchange(flowrate=0, cp1=4200, tp1=20, cp2=4200, tp2=50)) # sp1
    pp.append(PulsePeriod())
    fr.append(FlowRate()) # define pulse coeff
####
#from droidcontroller.nagios import NagiosMessage # paralleelteated otse starmani
#nagios = NagiosMessage(mac, 'service_energy_ee', nagios_ip='62.65.192.33', nagios_port=50000)
#udp.set_copynotifier(nagios.output_and_send) # mida kasutada teadete koopia saatmiseks nagiosele. kui puudub, ei saada koopiaid.
####

ts = time.time() # needed for manual function testing
ts_app = ts
flowperiod = [None, None, None]
el_energylast = [0, 0, 0] # None ei ole alguseks hea, esimene ja ka koik jargmised lahutamised failivad
pump_old = [0, 0, 0]

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