import m_file
import socket
from os import path

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
        #self.conf = self.ini.read(path.join(data_dir, 'conf.json'))
        #print(path.join(data_dir, 'conf.json'))
        #self.conf = self.ini.read('conf.json')
        #self.ip = self.conf['host']
        #self.port = self.conf['port']
    def load_conf(self, data_dir):
        self.conf = self.ini.read(path.join(data_dir, 'conf.json'))
        print(path.join(data_dir, 'conf.json'))
        self.ip = self.conf['host']
        self.port = self.conf['port']
    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
    def disconnect(self):
        self.client_socket.close()
    def reconnect(self):
        pass