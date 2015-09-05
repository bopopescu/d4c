APVER='ioloop app test 28.08.2015'
''' highest script for a customer '''

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from droidcontroller.controller_app import * 

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)


class CustomerApp(object):
    def __init__(self): # create instances
        ''' comm, udp. controllerapp jne '''
        self.ca = ControllerApp(self.app)
    def app(self, appinstance):
        ''' customer-specifric things '''
        res= 0
        print('app here')
        res = 0
        return res
        # self.ca is also usable here

cua = CustomerApp() # test like cua.ca.udp_sender()
    
if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on

