APVER='monitor/iomain_monitor 21.10.2015'
''' highest script for an application '''

import os, sys, time, traceback
from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import * # arranges modbus and server comms
#from droidcontroller.statekeeper import * # should you need some state management

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)


class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''
        self.ca = ControllerApp(self.app, mba = 1, mbi = 0)
        print('ControllerApp instance created')
        
    def app(self, appinstance, attentioncode = 0):
        ''' customer-specific things '''
        print('app here')
        res = 0
        return res
        # self.ca is also usable here

cua = CustomerApp() # test like cua.ca.udp_sender()
udp.setAPVER(APVER) # app version to be sent to server on connectivity up

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on
    
# testi cua.ca.commtest()

