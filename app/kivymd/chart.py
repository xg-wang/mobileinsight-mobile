# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.properties import ListProperty, OptionProperty, BooleanProperty,NumericProperty,StringProperty
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.theming import ThemableBehavior
from kivy.uix.progressbar import ProgressBar
from kivymd.progressbar import MDProgressBar
from kivy.clock import Clock
import random
from kivy.uix.boxlayout import BoxLayout

Builder.load_string('''
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import MDLabel kivymd.label.MDLabel
<MDProgressLine>:
    canvas:
        Clear
        Color:
            rgba:  self.theme_cls.divider_color
        Rectangle:
            size:   dp(18),self.height
            pos:   self.center_x,self.y-dp(24)
            
        
            
        Color:
           
            rgba:  get_color_from_hex(self.rgbr)
        Rectangle:
            size:    sp(18), self.height*self.value_normalized
                
            pos:   
                self.center_x,self.y-dp(24)

<MDChart>:
    BoxLayout:
        spacing: -375
        MDProgressLine:
            
            value: root.values[0]

        MDProgressLine:
           
            value:root.values[1]

        MDProgressLine:
            
            value: root.values[2]
        MDProgressLine:
           
            value: root.values[3]
        MDProgressLine:
            
            value: root.values[4]
        MDProgressLine:
            value: root.values[5]
        MDProgressLine:
            value: root.values[6]
        MDProgressLine:
            value: root.values[7]
        MDProgressLine:
            value: root.values[8]
        MDProgressLine:
            value: root.values[9]
        
        
        

''')


class MDProgressLine(ThemableBehavior, ProgressBar):
    reversed = BooleanProperty(False)
    ''' Reverse the direction the progressbar moves. '''
    orientation = OptionProperty('horizontal', options=['horizontal', 'vertical'])
    ''' Orientation of progressbar'''
    rgbr = StringProperty("FF0000")
    test = BooleanProperty(False)
    #rgbr = OptionProperty('FF0000', 
        #options=['FF0000','00FF00','0000FF'])
    alpha =NumericProperty(.9)
    

    def on_rgbr(self,instance,value):
        # self.rgbr = value
        # print "on_rgbr"
        #print self.rgbr
        r1,r2=255,255
        g1,g2=204,0
        b1,b2=0,0
        r=int((r1*self.value+r2*(100-self.value))/100)
        g=int((g1*self.value+g2*(100-self.value))/100)
        b=int((b1*self.value+b2*(100-self.value))/100)
        
        self.rgbr= hex(r)[2:].zfill(2)+hex(g)[2:].zfill(2)+hex(b)[2:].zfill(2)
    def on_value(self,instance,value):
        r1,r2=255,255
        g1,g2=204,0
        b1,b2=0,0
        r=int((r1*self.value+r2*(100-self.value))/100)
        g=int((g1*self.value+g2*(100-self.value))/100)
        b=int((b1*self.value+b2*(100-self.value))/100)
        
        self.rgbr= hex(r)[2:].zfill(2)+hex(g)[2:].zfill(2)+hex(b)[2:].zfill(2)
    
class MDChart(BoxLayout):
    current = NumericProperty(0)
    values = ListProperty([0,0,0,0,0,0,0,0,0,0])
    

    def on_current(self,instance,value):
         
         self.values.append(self.current)
         self.values.pop(0)

    def on_values(self,instance,value):
        pass
    


        

    
            
    
if __name__ == '__main__':
    from kivy.app import App
    from kivymd.theming import ThemeManager
    
    class ChartApp(App):
        theme_cls = ThemeManager()
        rvalue = NumericProperty(40)

        def callback(self,dt):
            self.rvalue =random.random()*100
            print self.rvalue
        def on_rvalue(self,instance,value):
             pass


        def build(self):
            Clock.schedule_interval(self.callback, 1)
            return Builder.load_string("""#:import MDSlider kivymd.slider.MDSlider
        #:import MDLabel kivymd.label.MDLabel
        #:import MDProgressBar kivymd.progressbar 
        
BoxLayout:
    orientation:'vertical'
    padding: '8dp'
    MDSlider:
        id:slider
        min:0
        max:100
        value: 10
        
    # MDProgressLine:
    #     value: app.rvalue
    #     rgbr:"00FF00"
    MDChart:
        current:app.rvalue
        #values: [0,0,0,0,0,0]

       
    
    
            
        
""")
            

    ChartApp().run()
