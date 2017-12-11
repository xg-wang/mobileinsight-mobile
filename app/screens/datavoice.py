from . import MobileInsightScreenBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from main_utils import Event
from kivy.logger import Logger

Builder.load_file('screens/datavoice.kv')

class DatavoiceScreen(MobileInsightScreenBase):

    EMM_State = BooleanProperty(False)
    ESM_State = BooleanProperty(False)

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
        Logger.info('DataVoiceScreen: ' + decoded.data)
        string = decoded.data
        if string == 'ESM_CON':
            self.ESM_State = True
        elif string == 'ESM_DISCON':
            self.ESM_State = False
        elif string == 'EMM_REGISTERED' or string == 'EMM_REGISTERED_INITIATED':
            self.EMM_State = True
        elif string == 'EMM_DEREGISTERED' or string == 'EMM_DEREGISTERED_INITIATED':
            self.EMM_State = False
