from . import MobileInsightScreenBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from main_utils import Event

Builder.load_file('screens/connectivity.kv')

class ConnectivityScreen(MobileInsightScreenBase):

    Short_DRX_State = BooleanProperty(False)
    CRX_State = BooleanProperty(False)
    Long_DRX_State = BooleanProperty(False)
    LTE_RRC_IDLE_State = BooleanProperty(True)

    def on_Short_DRX_State(self,instance,value):
    	pass

    def on_CRX_State(self,instance,value):
    	pass
    
    def on_Long_DRX_State(self,instance,value):
    	pass

    def on_LTE_RRC_IDLE_State(self,instance,value):
    	pass

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
        if string == 'CRX':
            self.CRX_State = True
            self.Short_DRX_State = False
            self.Long_DRX_State = False
            self.LTE_RRC_IDLE_State = False
        elif string == 'LONG_DRX':
            self.CRX_State = False
            self.Short_DRX_State = False
            self.Long_DRX_State = True
            self.LTE_RRC_IDLE_State = False
        elif string == 'SHORT_DRX':
            self.CRX_State = False
            self.Short_DRX_State = True
            self.Long_DRX_State = False
            self.LTE_RRC_IDLE_State = False
        else:
            self.CRX_State = False
            self.Short_DRX_State = False
            self.Long_DRX_State = False
            self.LTE_RRC_IDLE_State = True
