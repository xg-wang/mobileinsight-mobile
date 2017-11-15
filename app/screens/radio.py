from . import MobileInsightScreenBase
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty


Builder.load_file('screens/radio.kv')

class RadioScreen(MobileInsightScreenBase):

    current_log = StringProperty('')

    def configure_coordinator(self):
        self.coordinator.register_analyzer('LteNasAnalyzer')
        self.coordinator.register_analyzer('LteRrcAnalyzer')
        self.coordinator.register_callback(self._demo_callback)

    def _demo_callback(self, event):
        Logger.info('DemoScreen: ' + str(event))
        string = str(event)
        Logger.info('DemoScreen: ' + 'show event')
        self.current_log = string
