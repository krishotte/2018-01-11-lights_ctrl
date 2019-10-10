# simple kivy app for lithts intensity control
# socket operated communication
import socket
import m_file
import m_socket
import m_logger
import kivy

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from os import path
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.factory import Factory

file_path = path.join(path.dirname(path.realpath(__file__)), 'lights_ctrl.kv')
print('loading... ' + file_path)
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())
file_path = path.join(path.dirname(path.realpath(__file__)), 'lights_setup.kv')
print('loading... ' + file_path)
with open(file_path, encoding='utf-8') as f:
    Builder.load_string(f.read())

class Disconn1(Label):
    pass
class Conn1(Disconn1):
    pass
class STWidget(RelativeLayout):
    ch1_vals = ListProperty()
    ch2_vals = ListProperty()
    elog = ObjectProperty()
    sldr = ObjectProperty()
    state_ch1 = StringProperty()
    state_ch2 = StringProperty()
    ctrl_label = ObjectProperty()  
class Lights_Setup(BoxLayout):
    ch1_vals = ListProperty()
    ch2_vals = ListProperty()


class MainWidget(FloatLayout):                      #root widget class - main functionality - GUI
    disconn1 = Disconn1()
    conn1 = Conn1()
    light_ctrl = Factory.STWidget()
    light_setup = Factory.Lights_Setup()

    def show_disconn(self, *args):
        'shows disconnected label'
        try:
            #self.add_widget(self.disconn1)
            self.light_ctrl.ctrl_label.add_widget(self.disconn1)
            self.aprint('disconn widget just displayed')
        except:
            self.aprint('disconn widget already displayed')

    def hide_disconn(self, *args):
        'hides disconnected label'
        self.light_ctrl.ctrl_label.remove_widget(self.disconn1)

    def show_conn(self, *args):
        'shows connected label'
        try:
            self.light_ctrl.ctrl_label.add_widget(self.conn1)
            self.aprint('conn widget just displayed')
        except:
            self.aprint('conn widget already displayed')

    def hide_conn(self, *args):
        'hides connected label'
        self.light_ctrl.ctrl_label.remove_widget(self.conn1)

    def show_ctrl(self):
        'shows main control widget'
        self.remove_widget(self.light_setup)
        self.add_widget(self.light_ctrl)
        self.aprint('ctrl shown')
        #self.light_setup.ch1_vals = self.light_ctrl.ch1_vals

    def show_setup(self):
        'shows setup widget'
        self.remove_widget(self.light_ctrl)
        self.add_widget(self.light_setup)
        self.aprint('setup shown')

    def aprint(self, message):
        'prints message to standard output and to kivy log'
        print('aprint message: ' + message)
        self.light_ctrl.elog.text = self.log1.addline(message)

    def load_settings(self):
        'loads settings.json if exists'
        settings = m_file.ini2().read(path.join(self.datadir, 'settings.json'))
        self.aprint('settings: ' + str(settings))
        try:
            self.light_ctrl.ch1_vals = settings['ch1_vals']
            self.aprint('ch1_vals found: ' + str(settings['ch1_vals']))
        except(KeyError):
            self.light_ctrl.ch1_vals = [100, 70, 40, 20, 0]
            self.aprint('key ch1_vals not found, using default')
        try:
            self.light_ctrl.ch2_vals = settings['ch2_vals']
            self.aprint('ch2_vals found: ' + str(settings['ch2_vals']))
        except(KeyError):
            self.light_ctrl.ch2_vals = [100, 70, 40, 20, 0]
            self.aprint('key ch2_vals not found, using default')
        if not settings:
            self.save_settings() #datadir)

    def save_settings(self):
        'saves GUI setup to settings.json'
        self.aprint('saving settings.json')
        settings = {
            'ch1_vals': self.light_ctrl.ch1_vals,
            'ch2_vals': self.light_ctrl.ch2_vals
        }
        m_file.ini2().write(path.join(self.datadir, 'settings.json'), settings)

    def open(self, datadir):                             #inits app
        "initializes main widget class"
        self.add_widget(self.light_ctrl)
        self.s_data = m_socket.socket_data()            #socket data
        self.s_conn = m_socket.socket_connection()      #socket connection
        self.log1 = m_logger.log(25)                    #inits logger
        #Clock.schedule_interval(self.test_autolabels, 3)
        self.datadir = datadir
        self.load_settings() #datadir)
        self.light_setup.ch1_vals = self.light_ctrl.ch1_vals
        self.light_setup.ch2_vals = self.light_ctrl.ch2_vals
        self.tfields_update()

    def data_exchange(self, cmd, chn, duties):
        'exchanges data throught the socket'
        try:
            sockstr = self.s_data.constr(cmd, chn, duties)
            self.aprint('sending... ' + str((cmd, chn, duties)))
            self.s_conn.client_socket.send(sockstr)
            recv1 = self.s_conn.client_socket.recv(32)
            curr_setup = self.s_data.deconstr(recv1)
            self.aprint('receiving... ' + str(curr_setup))
        except:
            curr_setup = (4, 0, [0, 0, 0, 0])
            self.aprint('communication error')
        return curr_setup

    def light_setup_get(self, *args):                  #gets current ESP32 chn setup
        "gets current configuration"
        status = self.s_conn.connect()
        #sockstr = self.s_data.constr(1, 0, [0, 0, 0, 0])
        if status == True:
                Clock.schedule_once(self.hide_disconn, 0)
                Clock.schedule_once(self.show_conn, 0)
                self.curr_setup = self.data_exchange(1, 0, [0, 0, 0, 0])
                self.s_conn.disconnect()
                Clock.schedule_once(self.hide_conn, 1)
                self.light_ctrl.state_ch1 = str(self.curr_setup[2][0])
                self.light_ctrl.state_ch2 = str(self.curr_setup[2][1])
        else:
            self.curr_setup = (4, 0, [0, 0, 0, 0])
            Clock.schedule_once(self.show_disconn, 0)

    def light_chn_upd(self, chn, duty):
        'updates lighting level for single channel, simplified'
        self.aprint('------------------')
        self.light_setup_get()
        if self.curr_setup[0] != 4:
            status = self.s_conn.connect()
            if status == True:
                Clock.schedule_once(self.hide_disconn, 0)
                Clock.schedule_once(self.show_conn, 0)
                duties = []
                for i in range(0, 4):
                        if chn == i:
                            duties.append(duty)
                        else:
                            duties.append(self.curr_setup[2][i])
                self.curr_setup = self.data_exchange(2, chn, duties)
                self.s_conn.disconnect()
                self.slider_update()
                Clock.schedule_once(self.hide_conn, 1)
            else:
                Clock.schedule_once(self.show_disconn, 0)
                self.aprint('could not connect, check network config')
        else:
            self.aprint('could not connect, check network config')

    def slider_update(self, *args):
        "updates slider value according to toggle button pressed"
        self.light_setup_get()
        self.TGlBtn = -1
        self.aprint("curr setup: " + str(self.curr_setup))
        if self.light_ctrl.ids.TGlBtn1.state == 'down':
            self.TGlBtn = 1
        elif self.light_ctrl.ids.TGlBtn2.state == 'down':
            self.TGlBtn = 2
        if self.TGlBtn > 0:
            self.light_ctrl.ids.sldr1.value = self.curr_setup[2][self.TGlBtn -1]
            self.aprint('slider value: ' + str(self.curr_setup[2][self.TGlBtn -1]))
        self.aprint('TGlBtn value: ' + str(self.TGlBtn))

    def slider_move(self):
        "updates light intensity according to slider value"
        #self.slider_update()
        if self.TGlBtn > 0:
            self.light_chn_upd(self.TGlBtn -1, int(self.light_ctrl.sldr.value))

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
        'validates and updates ctrl widget button values'
        self.aprint('ch1_vals: ' + str(self.light_setup.ch1_vals))
        self.tfields_update()
        a = []
        for i in range(5):
            if (int(self.tfields[i]) <= 100) and (int(self.tfields[i]) >= 0):
                a.append(self.tfields[i])
            else:
                a.append(self.light_ctrl.ch1_vals[i])
        self.aprint('ch1_vals to update:' + str(a))
        self.light_ctrl.ch1_vals = a
        self.aprint('ch1_vals: ' + str(self.light_setup.ch1_vals))
        self.tfields_update()
        b = []
        for i in range(5):
            if (int(self.tfields[i+5]) <= 100) and (int(self.tfields[i+5]) >= 0):
                b.append(self.tfields[i+5])
            else:
                b.append(self.light_ctrl.ch2_vals[i])
        self.aprint('ch2_vals to update:' + str(b))
        self.light_ctrl.ch2_vals = b
        self.aprint('ch2_vals: ' + str(self.light_setup.ch2_vals))
        self.save_settings()
        self.show_ctrl()
                
class Lights_Ctrl1(App):                        #app class
    def build(self):
        r_widg = MainWidget()
        r_widg.open(self.user_data_dir)                           #creates plots in graph
        r_widg.s_conn.load_conf(self.user_data_dir)
        Clock.schedule_once(r_widg.slider_update, 2) #light_setup_get, 2)
        #r_widg.light_setup_get()
        #r_widg.test()
        Window.size = (320, 700)
        return r_widg
if __name__ == "__main__":                      #runs app
    Lights_Ctrl1().run()
