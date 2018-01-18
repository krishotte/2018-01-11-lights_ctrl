# socket controlled lights
# simple kivy app for controll
import socket
import m_file

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.carousel import Carousel

class socket_data:                              
    """
    data structure for socket communication
    cmd:
        1 - get current setup
        2 - update 'chn' channel setup
        3 - response - OK
        4 - response - error
        5 - success
    """
    def __init__(self):
        self.cmd = 0                            #command
        self.chn = 0                            #channel
        self.duties = []                        #all channels values
        self.pwms = []                          #all channels pwms
        self.str1 = []                          #list of values of decoded binary string
    def constr(self, cmd, chn, duties):
        """
        cunstructs byte string for socket communication
        """
        self.strdata = str(hex(cmd)).encode() + str(hex(chn)).encode() + str(hex(0)).encode() + str(hex(0)).encode()
        for duty in duties:
            pwm = (duty * 255)//100
            self.strdata = self.strdata + str(hex(pwm)).encode()
        return self.strdata
    def deconstr(self, strg):
        """
        deconstructs data from socket byte string
        """
        self.duties.clear()
        self.pwms.clear()
        self.str1 = strg.decode().split('0x')
        self.cmd = int(self.str1[1], 16)
        self.chn = int(self.str1[2], 16)
        for i in range(5, 9):
            self.duties.append(((int(self.str1[i], 16) + 1) * 100)//255)
            self.pwms.append(int(self.str1[i], 16))
        return (self.cmd, self.chn, self.duties)

class socket_connection:                        
    """
    class for handling socket connection
    """
    def __init__(self):
        #self.ip = '192.168.12.101'
        #self.ip = '192.168.2.215' #'192.168.64.108' #'5CG6085LLT' #'192.168.64.107'
        #self.port = 8003
        self.ini = m_file.ini()
        self.conf = self.ini.read('conf.json')
        self.ip = self.conf['host']
        self.port = self.conf['port']
    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
    def disconnect(self):
        self.client_socket.close()
    def reconnect(self):
        pass

class STWidget(BoxLayout):                      #root widget class - main functionality - GUI
    #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def open(self):                             #inits plots
        """
        initializes main widget class
        """
        self.s_data = socket_data()                      #socket data
        self.s_conn = socket_connection()                #socket connection
        self.ids.eventlog.text = 'LightsCtrl v 0.1\n--------------------------'

    def light_update(self, duties):
        """
        obsolete function for basic lights control
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.2.218', 8001))
        self.client_socket.send(duties)
        self.client_socket.close()

    def light_update_cmd(self, chn, duty):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.2.218', 8001))
        #self.cur_setup = self.client_socket.recv(8)
        self.client_socket.send(duty)
        self.client_socket.close()

    def light_setup_get(self):                  #gets current ESP32 chn setup
        self.client_socket.connect(('192.168.2.218', 8001))
        self.s_data.constr(1, 0, [100, 70, 50, 20])
        self.curr_setup = self.client_socket.recv(32)

    def light_chn_upd(self, chn, duty):
        """
        update lighting level for single channel
        """
        done = False
        count = 0
        sockstr = self.s_data.constr(1, 0, [0, 0, 0, 0])
        print('current setup request: ', sockstr)
        while done == False and count < 3:
            count += 1
            duties = []
            pwms = []
            self.s_conn.connect()
            self.s_conn.client_socket.send(sockstr)                     #get current setup
            self.recv1 = self.s_conn.client_socket.recv(32)
            self.curr_setup = self.s_data.deconstr(self.recv1)
            print('received: ', self.recv1, '; ', self.curr_setup)      #print current setup
            for i in range(0, 4):
                if chn == i:
                    duties.append(duty)
                else:
                    duties.append(self.curr_setup[2][i])
            print('duties to update: ', duties)
            sockstr = self.s_data.constr(2, chn, duties)
            print('sockstr to send: ', sockstr)
            self.s_conn.client_socket.send(sockstr)                     #update current setup
            self.recv1 = self.s_conn.client_socket.recv(32)             #get updated setup
            self.curr_setup = self.s_data.deconstr(self.recv1)
            print('updated setup received: ', self.recv1, '; ', self.curr_setup)
            print('--pwms: ', self.s_data.pwms)
            if (self.curr_setup[0] == 3) and (self.curr_setup[2] == self.s_data.duties):
                sockstr = self.s_data.constr(5, 0, [0, 0, 0, 0])
                self.s_conn.client_socket.send(sockstr)
                print('success sent: ', sockstr)
                done = True
            else:
                pass
            self.s_conn.disconnect()

    def test(self):            
        """
        testing class
        """
        #sockstr = self.s_data.constr(1, 0, [100, 70, 50, 20])
        #print(sockstr)
        sockstr = self.s_data.constr(2, 1, [100, 95, 80, 30])
        #print(sockstr)
        #print(self.s_data.deconstr(sockstr))
        #
        #self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client_socket.connect(('5CG6085LLT', 8003))
        self.s_conn.connect()
        self.s_conn.client_socket.send(sockstr)
        #self.recv1 = self.s_conn.client_socket.recv(32)
        #print('received: ', self.recv1)
        self.s_conn.disconnect()
        print('--------')
        #self.light_chn_upd(1, 25)

class Lights_Ctrl(App):                        #app class
    def build(self):
        r_widg = STWidget()
        r_widg.open()                           #creates plots in graph
        #r_widg.test()
        return r_widg
            
if __name__ == "__main__":                      #runs app
    Lights_Ctrl().run()
