from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from os import path
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty
from kivy.factory import Factory
from kivy.properties import ListProperty

file_path = path.join(path.split(path.dirname(path.realpath(__file__)))[0], 'lights_ctrl.kv')
print('loading... ' + file_path)
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())
file_path = path.join(path.split(path.dirname(path.realpath(__file__)))[0], 'lights_setup.kv')
print('loading... ' + file_path)
with open(file_path, encoding='utf-8') as f:
    Builder.load_string(f.read())

class STWidget(RelativeLayout):
    ch1_vals = ListProperty()
    ch2_vals = ListProperty()
    elog = ObjectProperty()
    sldr = ObjectProperty()
    state_ch1 = StringProperty()
    state_ch2 = StringProperty()
    
class Lights_Setup(BoxLayout):
    ch1_vals = ListProperty()
    ch2_vals = ListProperty()
    
class MainVidget(RelativeLayout):
    light_ctrl = Factory.STWidget()
    light_setup = Factory.Lights_Setup()
    def open(self):
        self.add_widget(self.light_ctrl)
        self.light_ctrl.ch1_vals = [100, 70, 40, 20, 0]
        self.light_ctrl.ch2_vals = [100, 70, 40, 20, 0] #['100', '70', '40', '20', '0']
        self.light_setup.ch1_vals = [100, 70, 40, 20, 0]#['100', '70', '40', '20', '0']
        self.light_setup.ch2_vals = [100, 70, 40, 20, 0]
        self.tfields_update()
    def show_ctrl(self):
        self.remove_widget(self.light_setup)
        self.add_widget(self.light_ctrl)
        print('ctrl shown')
    def show_setup(self):
        self.remove_widget(self.light_ctrl)
        self.add_widget(self.light_setup)
        print('setup shown')
    def tfields_update(self):
        self.tfields = [
            self.light_setup.ids.ch1a.text,
            self.light_setup.ids.ch1b.text,
            self.light_setup.ids.ch1c.text,
            self.light_setup.ids.ch1d.text,
            self.light_setup.ids.ch1e.text,
            self.light_setup.ids.ch2a.text,
            self.light_setup.ids.ch2b.text,
            self.light_setup.ids.ch2c.text,
            self.light_setup.ids.ch2d.text,
            self.light_setup.ids.ch2e.text
        ]
    def update_ctrl(self):
        print('ch1_vals: ' + str(self.light_setup.ch1_vals))
        self.tfields_update()
        a = []
        for i in range(5):
            if (int(self.tfields[i]) <= 100) and (int(self.tfields[i]) >= 0):
                a.append(self.tfields[i])
            else:
                a.append(self.light_ctrl.ch1_vals[i])
        print('ch1_vals to update:' + str(a))
        self.light_ctrl.ch1_vals = a
        self.show_ctrl()
        """self.light_setup.ch1_vals = [int(self.light_setup.ids.ch1a.text), int(self.light_setup.ids.ch1b.text), int(self.light_setup.ids.ch1c.text), 
            int(self.light_setup.ids.ch1d.text), int(self.light_setup.ids.ch1e.text)]
        print('ch1_vals updated: ' + str(self.light_setup.ch1_vals))
        self.light_ctrl.ch1_vals = self.light_setup.ch1_vals
        self.show_ctrl()"""
class Lights_Ctrl1(App):                        #app class
    def build(self):
        r_widg = MainVidget() #Factory.Lights_Setup() #Lights_Setup() #STWidget()
        r_widg.open()
        Window.size = (320, 700)
        return r_widg
    pass
if __name__ == "__main__":                      #runs app
    Lights_Ctrl1().run()