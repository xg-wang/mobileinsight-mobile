'''
Screens
=======

.. versionadded:: 4.0.0

Contains all available screens for the Mobile-Insight app.

TODO: more doc

'''
import kivy

from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivy.lang import Builder
from kivy.logger import Logger
from coordinator import COORDINATOR

Builder.load_string('''
<MobileInsightScreenBase>:
    ScrollView:
        do_scroll_x: False
        do_scroll_y: False
''')

class MobileInsightScreenBase(Screen):
    fullscreen = BooleanProperty(False)

    def __init__(self, **kw):
        super(MobileInsightScreenBase, self).__init__(**kw)
        self.coordinator = COORDINATOR
        self.configure_coordinator()
        Logger.info('screen: screen inited')
        self.coordinator.start()

    def configure_coordinator(self):
        '''
        Screens should override this method to setup the coordinator.
        1. specify monitor, analyzers name to the monitor
        2. register callback to analyzers to retrieve data for display
        '''
        raise NotImplementedError

    def on_enter(self):
        self.coordinator.start()

    def on_leave(self):
        # TODO: check kivy version? seems to be added since 1.6
        self.coordinator.stop()


from radio import RadioScreen
from connectivity import ConnectivityScreen
from dataplane import DataplaneScreen
from datavoice import DatavoiceScreen
from mobility import MobilityScreen
from theming import ThemingScreen

__all__ = ['RadioScreen', 'ConnectivityScreen', 'DataplaneScreen', 'DatavoiceScreen',\
            'MobilityScreen', 'ThemingScreen']
