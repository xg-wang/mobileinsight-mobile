from . import MobileInsightScreenBase
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.logger import Logger

from kivy.clock import Clock
import random

Builder.load_file('screens/radio.kv')

class RadioScreen(MobileInsightScreenBase):

    current_log = StringProperty('')
    rsrq = NumericProperty(0)
    rssi = NumericProperty(0)
    rsrp = NumericProperty(0)
    def configure_coordinator(self):
        self.coordinator.register_analyzer('LteNasAnalyzer')
        self.coordinator.register_analyzer('LteRrcAnalyzer')
        self.coordinator.register_callback(self._demo_callback)

    def _demo_callback(self, event):
        Logger.info('DemoScreen: ' + str(event))
        string = str(event)
        self.current_log = string[:20]


        
    def on_rsrq(self,instance,value):
        pass
    def on_rsrp(self,instance,value):
        pass
    def on_rssi(self,instance,value):
        pass
