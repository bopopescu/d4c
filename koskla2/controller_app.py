import sys
import tornado
import tornado.ioloop

from droidcontroller.acchannels import *
ac = ACchannels(in_sql = 'aicochannels.sql', readperiod = 0, sendperiod = 20) # ai and counters
from droidcontroller.dchannels import *
d = Dchannels(readperiod = 0, sendperiod = 180) # di and do. immediate notification on change, read as often as possible
# the previous block also generated sqlgeneral and uniscada instances, like s, udp, tcp

OSTYPE='archlinux'
print('OSTYPE',OSTYPE)

from droidcontroller.udp_commands import * # sellega alusta, kaivitab ka SQlgeneral
p = Commands(OSTYPE) # setup and commands from server
r = RegularComm(interval=120) # variables like uptime and traffic, not io channels

mac = udp.get_conf('mac', 'host_id.conf') # uniscada paneb ka enda jaoks kehtima
udp.setID(mac) # kontrolleri id
tcp.setID(mac) # kas tcp seda kasutabki?
udp.setIP('46.183.73.35') # '195.222.15.51') # mon server ip
udp.setPort(44445)

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)

class ControllerApp(object):
    ''' '''
    def __init__(self, app):
        self.app = app # client-specific main script
        interval_ms = 1000 # milliseconds
        self.loop = tornado.ioloop.IOLoop.instance()
        self.udpread_scheduler = tornado.ioloop.PeriodicCallback(self.udp_reader, 250, io_loop = self.loop)
        self.di_scheduler = tornado.ioloop.PeriodicCallback(self.di_reader, 100, io_loop = self.loop)
        self.ai_scheduler = tornado.ioloop.PeriodicCallback(self.ai_reader, 3000, io_loop = self.loop)
        self.cal_scheduler = tornado.ioloop.PeriodicCallback(self.cal_reader, 3600000, io_loop = self.loop)
        self.udpsend_scheduler = tornado.ioloop.PeriodicCallback(self.udp_sender, 180000, io_loop = self.loop)
        self.udpread_scheduler.start()
        self.di_scheduler.start()
        self.ai_scheduler.start()
        self.cal_scheduler.start()
        self.udpsend_scheduler.start()
        
        
    def udp_reader(self): # UDP reader
        print('reading udp')
        got = udp.udpread() # loeb ainult!
        if got != {} and got != None:
            self.got_parse(got) # see next def
    

    def got_parse(self, got):
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
            

    def di_reader(self): # DI reader
        print('reading di channels')
        res = d.doall()
        if res > 0:
            self.app_main() # without detected change in di signals ai (or timer based) app_main execution is enough

    def ai_reader(self): # AICO reader
        print('reading ai, co')
        ac.doall()
        self.app_main()

    def udp_sender(self): # UDP sender
        print('sending udp')
        udp.buff2server()
        self.reset_sender_timeout()

    def cal_reader(self): # gcal  refresh
        print('cal sync')

    def reset_sender_timeout(self):
        ''' Resetting ioloop timer '''
        print('timer reset')

    def app_main(self): # everything to do after reading. code in controller_app.py
        ''' ehk on vaja param anda mis muutus, may call udp_sender '''
        print('app_main')
        res = self.app(self) # self selleks, et vahet teha erinevatel kaivitustel, valjakutsutavale lisa param instanceid vms
        # if res... # saab otsustada kas saata vms.
        self.udp_sender()
        

