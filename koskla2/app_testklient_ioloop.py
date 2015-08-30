APVER='ioloop app test 28.08.2015'
''' highest script for a customer '''

from droidcontroller.uniscada import * # UDPchannel, TCPchannel
from controller_app import * # this is located in the current directory

import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger(__name__)


def app(appinstance):
    ''' customer-specifric things '''
    res= 0
    print('app here')
    res = 0
    return res

def init(): # create instances
    ''' comm, udp. controllerapp jne '''
    ca = ControllerApp(app)


tornado.ioloop.IOLoop.instance().start() # start your loop, event-based from now on

