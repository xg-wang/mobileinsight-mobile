'''
Screens
=======

.. versionadded:: 3.2.1

Contains all available screens for the Mobile-Insight app.

TODO: more doc

'''
import kivy

from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivy.lang import Builder
from coordinator import Coordinator

Builder.load_string('''
<MobileInsightScreenBase>:
    ScrollView:
        do_scroll_x: False
        do_scroll_y: False if root.fullscreen else (content.height > root.height - dp(16))
        AnchorLayout:
            size_hint_y: None
            height: root.height if root.fullscreen else max(root.height, content.height)
            GridLayout:
                id: content
                cols: 1
                spacing: '8dp'
                padding: '8dp'
''')

class MobileInsightScreenBase(Screen):
    fullscreen = BooleanProperty(False)

    def __init__(self, **kw):
        super(MobileInsightScreenBase, self).__init__(**kw)
        self.coordinator = Coordinator()
        self.configure_coordinator()

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

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(MobileInsightScreenBase, self).add_widget(*args)


from demo import DemoScreen

__all__ = ['DemoScreen']
