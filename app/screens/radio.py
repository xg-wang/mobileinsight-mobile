from . import MobileInsightScreenBase
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.logger import Logger

from main_utils import Event

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
        self.coordinator.register_callback(self._radio_callback)

    def _radio_callback(self, event):
        event = Event(event)
        if event.type_id == 'rsrp':
            self.rsrp = event.data
            self.rssi = self.rsrp - 141 # little hack
        if event.type_id == 'rsrq':
            self.rsrq = event.data


    def on_rsrq(self,instance,value):
        pass
    def on_rsrp(self,instance,value):
        pass
    def on_rssi(self,instance,value):
        pass
