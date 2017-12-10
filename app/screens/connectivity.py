from . import MobileInsightScreenBase
from kivy.lang import Builder
from main_utils import Event 

Builder.load_file('screens/connectivity.kv')

class ConnectivityScreen(MobileInsightScreenBase):
    
    def configure_coordinator(self):
        self.coordinator.register_analyzer('LteRrcAnalyzer')
        self.coordinator.register_callback(self._connectivity_callback)

    def _connectivity_callback(self, event):
        decoded = Event(event) 
        if decoded.type_id != 'RRC' and decoded.type_id != 'DRX': 
            return 
        Logger.info('ConnectivityScreen: ' + decoded.type_id) 
        Logger.info('String: ' + decoded.data)
        string = decoded.data 
