import kivy
kivy.require('1.4.0')

from kivy.lang import Builder
from mobile_insight.analyzer import LteNasAnalyzer, UmtsNasAnalyzer
from mobile_insight.monitor import OnlineMonitor
import traceback
from . import MobileInsightScreenBase
from kivy.logger import Logger

Builder.load_file('screens/demo.kv')

class DemoScreen(MobileInsightScreenBase):
    '''
    mimic NasAnalysis
    '''
    def configure_coordinator(self):
        # self.coordinator.monitor = OnlineMonitor()
        # lte = LteNasAnalyzer()
        # un = UmtsNasAnalyzer()
        # for analyzer in [lte, un]:
        #     analyzer.register_screen_cb(self._demo_callback)
        #     self.coordinator.register_analyzer(analyzer)

    def _demo_callback(self, event):
        Logger.info(event)

