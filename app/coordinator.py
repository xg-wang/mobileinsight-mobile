import android
import threading
from time import sleep
from kivy.lib.osc import oscAPI as osc
from kivy.utils import platform
from main_utils import OSCConfig
import traceback
from kivy.logger import Logger


class Coordinator(object):
    '''App side control center
    see control for detailed protocol
    '''
    def __init__(self):
        self._analyzers = []
        self._screen_callbacks = []
        self._service_ready = threading.Event()

    def register_analyzer(self, analyzer):
        self._analyzers.append(analyzer)

    def register_callback(self, callback):
        self._screen_callbacks.append(callback)

    def start(self):
        '''
        Start service to setup monitor, analyzers,
        use osc to listen for data update
        '''
        if platform != 'android':
            Logger.error('Platform is not android, start service fail.')
            return
        osc.bind(OSCConfig.oscid, self.event_callback, OSCConfig.event_addr)
        osc.bind(OSCConfig.oscid, self.control_callback, OSCConfig.control_addr)
        Logger.info('coordinator: coordinator bind to ' + OSCConfig.event_addr)
        listen_thread = threading.Thread(target=self.listen_osc, args=(OSCConfig.oscid,))
        listen_thread.start()
        Logger.info('coordinator: ' + 'listen thread starts')

        # TODO: analyzers msg should be separated from osc init
        argstr = ','.join(self._analyzers)
        self.send_control(argstr)


    def listen_osc(self, oscid):
        while True:
            osc.readQueue(thread_id=oscid)
            sleep(.5)

    def event_callback(self, message, *args):
        Logger.info('coordinator <RECV: event msg: ' + message[2])
        def G(f): return f(message[2])
        map(G, self._screen_callbacks)

    def control_callback(self, message, *args):
        # set the Event lock once service is ready
        Logger.info('coordinator <RECV: control msg: ' + message[2])
        self._service_ready.set()

    def send_control(self, message):
        def thread_target(msg):
            # wait for service ready event
            self._service_ready.wait()
            osc.sendMsg(OSCConfig.control_addr, dataArray=[str(msg),], port=OSCConfig.service_port)
            Logger.info('coordinator SEND>: control msg: ' + msg)
        send_thread = threading.Thread(target=thread_target, args=(message,))
        send_thread.start()

    def stop(self):
        Logger.info('coordinator: ' + '// stops does nothing right now')

# only create a singleton coordinator for app
# should always import this coordinator
COORDINATOR = Coordinator()
Logger.info('coordinator: created COORDINATOR')
