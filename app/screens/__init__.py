'''
Screens
=======

.. versionadded:: 3.2.1

Contains all available screens for the Mobile-Insight app.

TODO: more doc

'''
import kivy
kivy.require('1.4.0')

from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivy.lang import Builder

Builder.load_string('''
#:kivy 1.4.0

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

    def add_widget(self, *args):
        print 'Base add_widget called'
        print self
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(MobileInsightScreenBase, self).add_widget(*args)

from home import HomeScreen

__all__ = ['HomeScreen']
