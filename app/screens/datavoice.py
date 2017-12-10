from . import MobileInsightScreenBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from main_utils import Event 

Builder.load_file('screens/datavoice.kv')

class DatavoiceScreen(MobileInsightScreenBase):
    
    EMM_State = BooleanProperty(False)
    ESM_State = BooleanProperty(True)

    def on_EMM_State(self,instance,value):
    	pass

    def on_ESM_State(self,instance,value):
    	pass

    def configure_coordinator(self):
        self.coordinator.register_analyzer('LteNasAnalyzer')
        self.coordinator.register_callback(self._datavoice_callback)

    def _datavoice_callback(self, event):
        decoded = Event(event) 
        if decoded.type_id != 'EMM' and decoded.type_id != 'ESM': 
            return 
        Logger.info('DataVoiceScreen: ' + decoded.type_id) 
        Logger.info('String: ' + decoded.data)
        string = decoded.data 
        # self.EMM_State = string
        # self.ESM_State = string
