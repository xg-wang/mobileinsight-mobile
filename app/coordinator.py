import os
import sys

import android
import threading
from time import sleep
from kivy.lib.osc import oscAPI as osc
from kivy.clock import Clock
from kivy.utils import platform
from jnius import autoclass
from mobile_insight.analyzer import LteNasAnalyzer, UmtsNasAnalyzer
from mobile_insight.monitor import OnlineMonitor
from service import mi2app_utils
import traceback
from kivy.logger import Logger

service_port = 3000

class Coordinator(object):
    def __init__(self):
        self.title = ''
        self.description = ''
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
        Logger.info('argstr: ' + argstr)

        android.start_service(title=self.title,
                             description=self.description,
                             arg=argstr)
        osc.init()
        oscid = osc.listen(port=service_port)
        osc.bind(oscid, self.osc_callback, '/mobileinsight')
        Clock.schedule_interval(lambda *x: osc.readQueue(thread_id=oscid), .5)
        # while True:
        #     osc.readQueue(thread_id=oscid)
        #     sleep(.5)

    def stop(self):
        osc.dontListen()
        android.stop_service()

    def osc_callback(self, message, *args):
        Logger.info('osc: to coordinator: ' + message)
        def G(f): return f(message[2])
        map(G, self._screen_callbacks)
