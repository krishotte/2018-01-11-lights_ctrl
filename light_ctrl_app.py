# socket controlled lights
# simple kivy app for control
import socket
import m_file
import m_socket
import m_logger

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.carousel import Carousel
from kivy.properties import ObjectProperty

class STWidget(BoxLayout):                      #root widget class - main functionality - GUI
    elog = ObjectProperty()
    def open(self):                             #inits app
        "initializes main widget class"
        self.s_data = m_socket.socket_data()            #socket data
        self.s_conn = m_socket.socket_connection()      #socket connection
        self.log1 = m_logger.log(25)                    #inits logger
        self.ids.eventlog.text = self.log1.addline('LightsCtrl v 0.2\n--------------------------')
        
    def light_update(self, duties):
        "obsolete function for basic lights control"
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.2.218', 8001))
        self.client_socket.send(duties)
        self.client_socket.close()

    def light_setup_get(self):                  #gets current ESP32 chn setup
        'TODO'
        status = self.s_conn.connect()
        sockstr = self.s_data.constr(1, 0, [100, 70, 50, 20])
        if status == True:
                self.s_conn.client_socket.send(sockstr)                     #get current setup
                self.recv1 = self.s_conn.client_socket.recv(32)
                self.curr_setup = self.s_data.deconstr(self.recv1)

    def light_chn_upd(self, chn, duty):
        "update lighting level for single channel"
        done = False
        count = 0
        maxlines = self.elog.texture_size[1]//(self.elog.font_size*1.3)     #guess max log linecount
        self.log1.max_lines = maxlines
        print('eventlog maxlines: ', maxlines)
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

class Lights_Ctrl(App):                        #app class
    def build(self):
        r_widg = STWidget()
        r_widg.open()                           #creates plots in graph
        r_widg.s_conn.load_conf(self.user_data_dir)
        #r_widg.test()
        return r_widg
            
if __name__ == "__main__":                      #runs app
    Lights_Ctrl().run()
