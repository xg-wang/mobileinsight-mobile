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
    mimic rrcAnalysis
    '''
    def configure_coordinator(self):
        self.coordinator.title = 'DemoCoordinator'
        self.coordinator.description = 'This is the demo coordinator.'
        self.coordinator.monitor = 'OnlineMonitor'
        # self.coordinator.register_analyzer('WcdmaRrcAnalyzer')
        self.coordinator.register_analyzer('LteNasAnalyzer')
        # self.coordinator.register_analyzer('LteRrcAnalyzer')
        self.coordinator.register_callback(self._demo_callback)

    def _demo_callback(self, event):
        Logger.info('DemoScreen: {}'.format(str(event)))
