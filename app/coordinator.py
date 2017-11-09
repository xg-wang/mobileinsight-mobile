import android
import threading
from time import sleep
from kivy.lib.osc import oscAPI as osc
from kivy.utils import platform
from main_utils import OSCConfig
import traceback
from kivy.logger import Logger


class Coordinator(object):
    def __init__(self):
        self.monitor = None
        self._analyzers = []
        self._screen_callbacks = []

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
        argstr = ';'.join([self.monitor, ','.join(self._analyzers)])
        osc.sendMsg(OSCConfig.control_addr, dataArray=[argstr,])
        Logger.info('osc: send control msg ' + argstr)

        osc.bind(OSCConfig.oscid, self.osc_callback, OSCConfig.event_addr)
        Logger.info('osc: coordinator bind to ' + OSCConfig.event_addr)
        # listen_thread = threading.Thread(target=self.listen_osc, args=(oscid,))
        # listen_thread.start()
        # Logger.info('coordinator: ' + 'listen thread starts')

    # def listen_osc(self, oscid):
    #     while True:
    #         osc.readQueue(thread_id=oscid)
    #         sleep(.5)

    def stop(self):
        Logger.info('coordinator: ' + '// stops does nothing right now')

    def osc_callback(self, message, *args):
        Logger.info('osc <RECV: ' + message[2])
        def G(f): return f(message[2])
        map(G, self._screen_callbacks)

# only create a singleton coordinator for app
# should always import this coordinator
coordinator = Coordinator()
