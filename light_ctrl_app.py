# socket controlled lights
# simple kivy app for control
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
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from os import path

file_path = path.dirname(path.realpath(__file__)) + '\\lights_ctrl.kv'
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())

class Disconn1(Label):
    pass
class Conn1(Disconn1):
    pass
class STWidget(FloatLayout):                      #root widget class - main functionality - GUI
    disconn1 = Disconn1()
    conn1 = Conn1()
    elog = ObjectProperty()
    sldr = ObjectProperty()
    def show_disconn(self, *args):
        'shows disconnected label'
        try:
            self.add_widget(self.disconn1)
            print('disconn widget just displayed')
        except:
            print('disconn widget already displayed')
    def hide_disconn(self, *args):
        'hides disconnected label'
        self.remove_widget(self.disconn1)
    def show_conn(self, *args):
        'shows connected label'
        try:
            self.add_widget(self.conn1)
            print('conn widget just displayed')
        except:
            print('conn widget already displayed')
    def hide_conn(self, *args):
        'hides connected label'
        self.remove_widget(self.conn1)
    def open(self):                             #inits app
        "initializes main widget class"
        self.s_data = m_socket.socket_data()            #socket data
        self.s_conn = m_socket.socket_connection()      #socket connection
        self.log1 = m_logger.log(25)                    #inits logger
        #self.ids.eventlog.text = self.log1.addline('LightsCtrl v 0.2\n--------------------------')
        #Clock.schedule_interval(self.test_autolabels, 3)
    def data_exchange(self, cmd, chn, duties):
        'exchanges data throught the socket'
        try:
            sockstr = self.s_data.constr(cmd, chn, duties)
            self.ids.eventlog.text = self.log1.addline('sending... ' + str((cmd, chn, duties)))
            print('sending... ' + str((cmd, chn, duties)))
            self.s_conn.client_socket.send(sockstr)
            recv1 = self.s_conn.client_socket.recv(32)
            curr_setup = self.s_data.deconstr(recv1)
            self.ids.eventlog.text = self.log1.addline('receiving... ' + str(curr_setup))
            print('receiving... ' + str(curr_setup))
            self.ids.eventlog.text = self.log1.addline('sending... ' + str(sockstr))
            print('sending... ' + str(sockstr))
            self.s_conn.client_socket.send(sockstr)
            recv1 = self.s_conn.client_socket.recv(32)
            curr_setup = self.s_data.deconstr(recv1)
            self.ids.eventlog.text = self.log1.addline('receiving... ' + str(recv1))
            print('receiving... ' + str(recv1))
        except:
            curr_setup = (4, 0, [0, 0, 0, 0])
            self.ids.eventlog.text = self.log1.addline('communication error')
            print('communication error')
        return curr_setup
    def light_setup_get(self):                  #gets current ESP32 chn setup
        "gets current configuration"
        status = self.s_conn.connect()
        #sockstr = self.s_data.constr(1, 0, [0, 0, 0, 0])
        if status == True:
                Clock.schedule_once(self.hide_disconn, 0)
                Clock.schedule_once(self.show_conn, 0)
                self.curr_setup = self.data_exchange(1, 0, [0, 0, 0, 0])
                self.s_conn.disconnect()
                Clock.schedule_once(self.hide_conn, 1)
        else:
            self.curr_setup = (4, 0, [0, 0, 0, 0])
            Clock.schedule_once(self.show_disconn, 0)
    def light_chn_upd(self, chn, duty):
        'updates lighting level for single channel, simplified'
        print('------------------')
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
                self.ids.eventlog.text = self.log1.addline('could not connect, check network config')
                print('could not connect, check network config')
        else:
            self.ids.eventlog.text = self.log1.addline('could not connect, check network config')
            print('could not connect, check network config')
    def light_chn_upd_2(self, chn, duty):
        "obsolete - update lighting level for single channel"
        done = False
        count = 0
        maxlines = self.elog.texture_size[1]//(self.elog.font_size*1.3)     #guess max log linecount
        self.log1.max_lines = maxlines
        #print('eventlog maxlines: ', maxlines)
        sockstr = self.s_data.constr(1, 0, [0, 0, 0, 0])        #command to get current setup
        self.ids.eventlog.text = self.log1.addline('-------------------------------------------')
        self.ids.eventlog.text = self.log1.addline('current setup request: ' + str(sockstr))
        while done == False and count < 3:
            count += 1
            duties = []
            pwms = []
            status = self.s_conn.connect()
            if status == True:
                self.s_conn.client_socket.send(sockstr)                     #get current setup
                self.recv1 = self.s_conn.client_socket.recv(32)
                self.curr_setup = self.s_data.deconstr(self.recv1)
                self.ids.eventlog.text = self.log1.addline('received: ' + str(self.recv1) + '; ' + str(self.curr_setup))      #print current setup
                for i in range(0, 4):
                    if chn == i:
                        duties.append(duty)
                    else:
                        duties.append(self.curr_setup[2][i])
                self.ids.eventlog.text = self.log1.addline('duties to update: ' + str(duties))
                sockstr = self.s_data.constr(2, chn, duties)
                self.ids.eventlog.text = self.log1.addline('sockstr to send: ' + str(sockstr))
                self.s_conn.client_socket.send(sockstr)                     #update current setup
                self.recv1 = self.s_conn.client_socket.recv(32)             #get updated setup
                self.curr_setup = self.s_data.deconstr(self.recv1)
                self.ids.eventlog.text = self.log1.addline('updated setup received: ' + str(self.recv1) + '; ' + str(self.curr_setup))
                self.ids.eventlog.text = self.log1.addline('--pwms: ' + str(self.s_data.pwms))
                if (self.curr_setup[0] == 3) and (self.curr_setup[2] == self.s_data.duties):
                    sockstr = self.s_data.constr(5, 0, [0, 0, 0, 0])
                    self.s_conn.client_socket.send(sockstr)
                    self.ids.eventlog.text = self.log1.addline('success sent: ' + str(sockstr))
                    done = True
                else:
                    self.ids.eventlog.text = self.log1.addline("duties do not match, again")
                self.s_conn.disconnect()
            else:
                self.ids.eventlog.text = self.log1.addline('could not connect, check network config')
            self.slider_update()
    def slider_update(self):
        "updates slider value according to toggle button pressed"
        self.light_setup_get()
        self.TGlBtn = -1
        print("curr setup: ", str(self.curr_setup))
        if self.ids.TGlBtn1.state == 'down':
            self.TGlBtn = 1
        elif self.ids.TGlBtn2.state == 'down':
            self.TGlBtn = 2
        if self.TGlBtn > 0:
            self.ids.sldr1.value = self.curr_setup[2][self.TGlBtn -1]
            print('slider value: ', self.curr_setup[2][self.TGlBtn -1])
        print('TGlBtn value: ', self.TGlBtn)
    def slider_move(self):
        "updates light intensity according to slider value"
        #self.slider_update()
        if self.TGlBtn > 0:
            self.light_chn_upd(self.TGlBtn -1, int(self.ids.sldr1.value))
    def test(self):            
        """
        testing class
        """
        #sockstr = self.s_data.constr(1, 0, [100, 70, 50, 20])
        #print(sockstr)
        #sockstr = self.s_data.constr(2, 1, [100, 95, 80, 30])
        #print(sockstr)
        #print(self.s_data.deconstr(sockstr))
        #
        #self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client_socket.connect(('5CG6085LLT', 8003))
        #self.s_conn.connect()
        #self.s_conn.client_socket.send(sockstr)
        #self.recv1 = self.s_conn.client_socket.recv(32)
        #print('received: ', self.recv1)
        #self.s_conn.disconnect()
        print('eventlog texturesize: ', self.elog.texture_size)
        print('eventlog textsize: ', self.elog.text_size)
        maxlines = self.elog.texture_size[1]//(self.elog.font_size*1.5)
        print('eventlog max line count: ', maxlines)
        print('--------')
        self.log1 = m_logger.log(maxlines)
        #self.light_chn_upd(1, 25)
    def test1(self):
        print('sldr value: ', self.sldr.value)
    def test2(self, val1):
        self.ids.sldr1.value = val1
        print("toggle button state: ", self.ids.TGlBtn1.state, ';', self.ids.TGlBtn2.state)
    def test_autolabels(self, *args):
        'test scheduling of labels display'
        Clock.schedule_once(self.show_disconn, 0)
        Clock.schedule_once(self.hide_disconn, 1.5)
        Clock.schedule_once(self.show_conn, 2)
        Clock.schedule_once(self.hide_conn, 2.5)
class Lights_Ctrl1(App):                        #app class
    def build(self):
        r_widg = STWidget()
        r_widg.open()                           #creates plots in graph
        r_widg.s_conn.load_conf(self.user_data_dir)
        #r_widg.test()
        Window.size = (320, 700)
        return r_widg
if __name__ == "__main__":                      #runs app
    Lights_Ctrl1().run()
