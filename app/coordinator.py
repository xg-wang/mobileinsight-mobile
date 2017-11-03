import os
import sys

# Import MobileInsight modules
from android.broadcast import BroadcastReceiver
from jnius import autoclass
from mobile_insight.analyzer import LteNasAnalyzer, UmtsNasAnalyzer
from mobile_insight.monitor import OnlineMonitor
from service import mi2app_utils
import traceback
from kivy.logger import Logger

def on_broadcast(context, intent):
    '''
    This plugin is going to be stopped, finish closure work
    '''
    IntentClass = autoclass("android.content.Intent")
    intent = IntentClass()
    action = 'MobileInsight.Plugin.StopServiceAck'
    intent.setAction(action)
    try:
        mi2app_utils.pyService.sendBroadcast(intent)
    except Exception:
        Logger.exception(traceback.format_exc())

class Coordinator(object):
    def __init__(self):
        self._monitor = None
        self._analyzers = []
        self._screen_callbacks = []

    @property
    def monitor(self):
        return self._monitor

    @monitor.setter
    def monitor(self, m):
        # TODO: stop the previous monitor if exists
        if (self._monitor is not None):
            self._monitor.stop()
        self._monitor = m

    def register_analyzer(self, analyzer):
        self._analyzers.append(analyzer)

    def register_callback(self, callback):
        self._screen_callbacks.append(callback)

    def start(self):
        '''
        Start collecting
        '''
        if self.monitor is None:
            Logger.warn("Monitor not set for coordinator.")
            return
        cache_directory = mi2app_utils.get_cache_dir()
        log_directory = os.path.join(cache_directory, "mi2log")
        self.monitor.set_log_directory(log_directory)
        self.monitor.set_skip_decoding(False)
        for analyzer in self._analyzers:
            analyzer.set_source(self.monitor)

        br = BroadcastReceiver(
            on_broadcast, actions=['MobileInsight.Main.StopService'])
        br.start()
        self._monitor.run()

    def stop(self):
        # TODO: stop monitor
        self.monitor.stop()
        self._analyzers = []
        self._screen_callbacks = []
