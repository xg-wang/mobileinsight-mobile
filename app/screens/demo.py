import kivy
kivy.require('1.4.0')

from kivy.lang import Builder
from kivy.properties import StringProperty
from mobile_insight.analyzer import LteNasAnalyzer, UmtsNasAnalyzer
from mobile_insight.monitor import OnlineMonitor
from main_utils import Event
import traceback
from . import MobileInsightScreenBase
from kivy.logger import Logger

Builder.load_file('screens/demo.kv')

class DemoScreen(MobileInsightScreenBase):
    '''
    mimic rrcAnalysis
    '''

    current_log = StringProperty('')

    def configure_coordinator(self):
        self.coordinator.register_analyzer('LteNasAnalyzer')
        self.coordinator.register_analyzer('LteRrcAnalyzer')
        self.coordinator.register_callback(self._demo_callback)

    def _demo_callback(self, event):
        decoded = Event(event)
        Logger.info('DemoScreen: ' + decoded.type_id)
        if decoded.type_id != 'TYPE':
            return
        string = decoded.data
        self.current_log = string
