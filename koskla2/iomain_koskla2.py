APVER='koskla2/iomain_koskla2 21.10.2015'
''' highest script for an application. koskla2 heat pumps monitoring
testing
cua.ca() kaivitab siinse app


'''

import os, sys, time, traceback
from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import * # arranges modbus and server comms
#from droidcontroller.statekeeper import * # should you need some state management

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

ts = time.time()
ts_app = ts
el_energylast = [0, 0, 0] # None ei ole alguseks hea, esimene ja ka koik jargmised lahutamised failivad
pump_old = [0, 0, 0]
# FIXME - eelmised self.muutujateks? alloleva klassi init abil


from droidcontroller.heatflow import * # heat flow and energy
from droidcontroller.speedometer import * # alternative flowrate calc

he = []
fr = []
fr2 = [] #test speedometer abil
for i in range(3):
    if i < 2:
        he.append(HeatExchange(flowrate=0, cp1=4200, tp1=20, cp2=4200, tp2=50, unit='hWh')) # sp1, sp2 water
    else:
        he.append(HeatExchange(flowrate=0, cp1=3525, tp1=40, cp2=3604, tp2=80, unit='hWh')) # solar, 30% ethylene glykol, per litre! J/(l K)
        # see http://www.engineeringtoolbox.com/ethylene-glycol-d_146.html
    fr.append(FlowRate()) # define pulse coeff
    fr2.append(SpeedoMeter(windowsize=10)) # alternatiivne kulumootja vordluseks

class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''
        self.di_state = [None, None, None]
        di_state = [None, None, None]
        self.ca = ControllerApp(self.app, mba = 1, mbi = 0)
        print('ControllerApp instance created')


    def app(self, appinstance, attentioncode = 0): # attentioncode 1 = d, 2=a, 3= d+a
        ''' customer-specific things '''
        # self.ca is also usable here
        global ts, ts_app, el_energylast, pump_old # FIXME to self.var
        pump = [0, 0, 0]  # temporary list
        ##ts = time.time() # ajutine, testimiseks aega vaja
        #flowrate = 0
        
        try:
            di_state = s.get_value('D1W','dichannels')[0:3] # didebug svc, first 3 inputs are water meters w pulse output
            pump = s.get_value('D1W','dichannels')[3:6] # didebug svc, next 3 inputs are pumps on the same tube with previous water meters
            
            #change the pulse input order
            temp = di_state[0]
            di_state[0] = di_state[1]
            di_state[1] = temp
            
        except:
            log.warning('problem with reading D1W data, break out from app, di_state '+str(di_state))
            return 1
        
        
        metercoeff = [10, 10, 10] # litres per pulse
        flowfixed = [1.67, 1.28, 0.172] # l/s - esimesed 2 peaks olema 1.67 ehk 100 l/min

        for i in range(3):
            #fr[i].update(pump[i], di_state[i]) ## oli enne komment!  flow update! pulsse ei tohi vahele jatta
            if pump[i] == 1:
                fr2[i].start()
            else:
                fr2[i].stop()
            if di_state[i] != self.di_state[i]:
                if di_state[i] == 1:
                    fr2[i].count()
                self.di_state[i] = di_state[i]
                
            try:
                volumecount = int(ac.get_aivalue('V'+str(i+5)+'V',1)[0]) # to check and fix flowrate calc in case of edge missing
                if volumecount != None:
                    volumecount = volumecount / metercoeff[i]
                if volumecount > 1: # avoid trouble with volume jump when restoring later
                    msg = str( fr[i].output(pump[i], di_state[i], volumecount) )
                else:
                    msg = str( fr[i].output(pump[i], di_state[i]) )
                log.info('pump '+str(pump[i])+', di_state '+str(di_state[i])+', fr flowrate '+msg+', volumecount '+str(volumecount))
            except:
                log.warning('no valid data yet from svc V'+str(i+5)+'V.1' )
                #traceback.print_exc()

        if ts < ts_app + 5: # continue not too often...
            return 5

        # valistemperatuur avg 2 anduri alusel
        temps = ac.get_aivalues('T0W') # members 2 and 3 are sensor values
        if temps[1] != None and temps[2] != None and (abs(temps[1] - temps[2]) < 50):
            avgtemp = (temps[1] + temps[2]) / 2
            ac.set_airaw('T0W', 1, int(round(avgtemp,0))) # ddegC


        for i in range(3):
            #log.info('app_doall starting i '+str(i)) ###
            try:
                flowrate2 = fr[i].get_flow() # fr alusel
                flowrate3 = 10 * fr2[i].get_speed() # imp/sec * 10 L
                msg = 'pump '+str(pump)+', di_state '+str(di_state)+', flowrate '+str(flowrate2)+', fr2 flowrate '+str(flowrate3) # +', flowperiod '+str(flowperiod)
                log.info(msg) ##
                ac.set_airaw('F'+str(5+i)+'V', 1, int(1000 * flowrate2 * pump[i])) # ml/s
                
                if flowrate2 != None:
                    ac.set_airaw('PFW', i+1, int(1000 * flowrate2)) # ml/s
                else:
                    ac.set_airaw('PFW', i+1, 0) # asendame nulliga

                if he[i]:
                    #he[i].set_flowrate(flowfixed[i]) ## ajutine  = 5 imp 5 min jooksul kui 10 imp/l, 100 l /min. lyhikesed tootsyklid..
                    he[i].set_flowrate(flowrate2) # tegelik flowrate arvesse
                    if i == 0: # sp1
                        Ton = s.get_value('T51W','aicochannels')[0]
                        Tret = s.get_value('T51W','aicochannels')[1]
                        log.debug('i '+str(i)+' Ton '+str(Ton)+', Tret '+str(Tret)+', pump '+str(pump[i]))
                        hrout = he[i].output(pump[i], Ton/10.0, Tret/10.0) # params di_pump, Ton, Tret; returns tuple of W, J, s
                        log.info('i '+str(i)+', Tdiff '+str(int(Ton-Tret)/10)+', di_pump '+str(pump[i])+', he[0].output '+str(hrout))
                        hrpwr = hrout[0]
                        if hrpwr == None or pump[i] == 0: # he.output is sometimes >0 during di_pump == 1???
                            hrpwr = 0
                        if ac.set_airaw('H1PW', 1, int(hrpwr)) != 0: # instant heat pump POWER W into svc
                            log.warning('PROBLEM with raw setting for HP1W!')

                    elif i == 1: # sp2
                        Ton = s.get_value('T61W','aicochannels')[0]
                        Tret = s.get_value('T61W','aicochannels')[1]
                        log.info('i '+str(i)+' Ton '+str(Ton)+', Tret '+str(Tret)+', pump '+str(pump[i]))
                        hrout = he[i].output(pump[i], Ton/10.0, Tret/10.0) # params di_pump, Ton, Tret; returns tuple of W, J, s
                        hrpwr = hrout[0]
                        log.info('i '+str(i)+', Tdiff '+str((Ton-Tret)/10)+', di_pump '+str(pump[i])+', he[1].output '+str(hrout))
                        if hrpwr == None or pump[i] == 0:
                            hrpwr = 0
                        if ac.set_airaw('H2PW', 1, int(hrpwr)) != 0: # instant heat pump POWER W
                            log.warning('PROBLEM with raw setting for HP2W!')
                    elif i == 2: # solar
                        Ton = s.get_value('T65W','aicochannels')[0] # solar dn ja up temps
                        Tret = s.get_value('T65W','aicochannels')[1] # see annab none asemel ilusti eelmise value
                        log.info('i '+str(i)+' Ton '+str(Ton)+', Tret '+str(Tret)+', pump '+str(pump[i]))
                        hrout = he[i].output(pump[i], Ton/10.0, Tret/10.0) # solar to SPV
                        hrpwr = hrout[0]
                        log.info('i '+str(i)+', Tdiff '+str((Ton-Tret)/10)+', di_pump '+str(pump[i])+', he[2].output '+str(hrout))
                        if hrpwr == None or pump[i] == 0:
                            hrpwr  = 0
                        if ac.set_airaw('SPV', 1, int(hrpwr)) != 0: # instant heat solar power
                            log.warning('PROBLEM with raw setting for SPV!')
                    else:
                        log.warning('app_doall() invalid i '+srt(i))

                    log.info('app_doall i '+str(i)+', Ton '+str(Ton/10)+', Tret '+str(Tret/10)+', hrout '+str(hrout))

                    #cumulative energies with possible recovery from server
                    energy = hrout[1]
                    posenergy = hrout[3]
                    negenergy = hrout[4] # all hWh

                    #voimalikud kumul energia taastamised ???????
                    cumheat = ac.get_aivalues('H'+str(i+1)+'CW') # [] of member values. hWh
                    log.debug('cumheat in svc H'+str(i+1)+'CW '+str(repr(cumheat)))
                    if energy != None and posenergy != None and negenergy != None and len(cumheat) == 3:
                        if cumheat[0] != None and cumheat[0] > (energy + 10): # value in svc bigger than in instance, avoid avg effect
                            log.info('*** restoring cumulative energy to '+str(cumheat[0])+' plus '+str(energy)+' for he['+str(i)+'], svc H'+str(i+1)+'CW!')
                            energy += cumheat[0] #  liita vahepeale kogunenu, hWh!
                            he[i].set_energy(energy)

                        if cumheat[1] != None and cumheat[1] > (posenergy + 10):
                            posenergy += cumheat[1]
                            he[i].set_energypos(posenergy)

                        if cumheat[2] != None and abs(cumheat[2]) > (abs(negenergy) + 10):
                            negenergy += cumheat[2] # kas liita vahepeale kogunenule?
                            he[i].set_energyneg(negenergy)
                        else:
                            if energy == posenergy and negenergy != 0:
                                cumheat[2] = 0
                                negenergy = 0
                                he[i].set_energyneg(negenergy)
                                log.info('negenergy zeroed due to energy = posenergy')

                        ac.set_aivalues('H'+str(i+1)+'CW', [int(round(energy, 0)), int(round(posenergy, 0)), int(round(negenergy, 0))]) # hWh
                        log.info('new cumulative heat energy hWh in H'+str(i+1)+'CW set to: '+str(int(energy))+', pos '+str(int(posenergy))+', neg '+str(int(negenergy)))
                    else:
                        log.warning('cumheat or energy not valid yet for he'+str(i)+' set_energy(), cumheat '+str(cumheat)+', energy '+str(energy))

                    if i < 2: # heat pump
                        if pump[i] != pump_old[i]: # heat pump just stopped, calc COP!
                            if pump[i] == 1:
                                log.info('heat pump '+str(i+1)+' started')
                                if el_energylast[i] == 0: # algseis seadmata
                                    el_energylast[i] = ac.get_aivalue('E'+str(i+1)+'CV', 1)[0]  # restore cumulative el energy hWh
                                    log.info('*** restored el_energylast['+str(i)+'] to hWh '+str(el_energylast[i]))

                            else: # stopped
                                log.info('heat pump '+str(i+1)+' stopped, new COP calc will follow')
                                ## COP & energy calculation
                                lastenergy = he[i].get_energylast() # hWh
                                el_energy = ac.get_aivalue('E'+str(i+1)+'CV', 1)[0] # cumulative el energy hWh
                                el_delta = el_energy - el_energylast[i] # hWh
                                el_energylast[i] = el_energy # keep in global variable until next hp stop
                                log.info('COP calc based on hWh el_delta '+str(el_delta)+' and lastenergy '+str(lastenergy))
                                if el_delta > 0 and (lastenergy > el_delta / 5) and (lastenergy < 10 * el_delta): # avoid division with zero and more
                                    ac.set_airaw('CP'+str(i+1)+'V', 1, int(round(10 * lastenergy / el_delta, 0))) # calculated for last cycle cop, x10
                                    log.info('last heat pump '+str(i+1)+' COP '+str(round(lastenergy / el_delta, 0))+' ('+str(lastenergy)+' / '+str(el_delta)+')')
                                else:
                                    log.warning('skipped COP calc for pump '+str(i+1)+' due to heat/el '+str(lastenergy)+' / '+str(el_delta))
                                    # something to restore to avoid cop loss after restart?

                else:
                    log.warning('NO he['+str(i)+'] instance!')

            except:
                log.warning('heatflow/power calculation failed')
                traceback.print_exc()
        pump_old = pump # []
        ts_app = ts
        return 0


    def test(self):
        ''' test everything once. use: cua.test() '''
        cua.ca.commtest()
        cua.ca.apptest()

##############
cua = CustomerApp() # test like cua.ca.udp_sender()


if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on

