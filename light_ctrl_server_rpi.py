import socket
import time
import pigpio

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
        return (self.cmd, self.chn, self.pwms)

class socket_connection:                        
    """
    class for handling socket connection
    """
    def __init__(self):
        #self.ip = '192.168.12.101'
        self.ip = '5CG6085LLT' #'192.168.64.107'
        self.port = 8003
    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
    def disconnect(self):
        self.client_socket.close()
    def reconnect(self):
        pass

class mypigpio:
    """
    class for handling Raspberry Pi GPIO PWM pins
    """
    def __init__(self):
        self.pwms = [50, 10, 0, 0]
        self.pins = [5, 6]
        self.pi = pigpio.pi()
        for i in range(2):
            self.pi.set_PWM_range(self.pins[i], 255)
            self.pi.set_PWM_dutycycle(self.pins[i], self.pwms[i])
    def getConfig(self):
        return self.pwms
    def setConfig(self, chn, pwms):
        print('setting pin:', self.pins[chn], '; setting pwm: ', pwms[chn])
        self.pi.set_PWM_dutycycle(self.pins[chn], pwms[chn])
        self.pwms[chn] = pwms[chn]
    def close(self):
        self.pi.stop()

sdata = socket_data()
pi = mypigpio()
print("initial pwms: ", pi.pwms)

#time.sleep(10)
#pi.close()

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a pub(lic host, and a well-known port
serversocket.bind(('192.168.2.215', 8003)) #socket.gethostname(), 8003))
print("server hostname: ", socket.gethostname())
# become a server socket
serversocket.listen(5)

while True:
    cmd1 = 0
    count = 0
    # accept connections from outside 
    (clientsocket, address) = serversocket.accept()
    # now do something with the clientsocket
    while (cmd1 != 5) and (count < 5):
        count += 1
        str1 = clientsocket.recv(32)
        print('count: ', count, 'str1: ', str1)
        try:
            a1 = sdata.deconstr(str1)
            cmd1 = a1[0]
            print(str1)
            print(a1)
            print('cmd: ', cmd1)
            if cmd1 == 1:
                str2 = sdata.constr(3,0,pi.pwms)
                print(str2)
                clientsocket.send(str2) #b'0x30x00x00x00xff0xb20x7f0xdd')
            elif cmd1 == 2:
                pi.setConfig(a1[1],a1[2])
                str2 = sdata.constr(3,0,pi.pwms)
                print(str2)
                clientsocket.send(str2) #b'0x30x00x00x00xdd0xb20x7f0xaa')
            elif cmd1 == 5:
                print('success')
                #clientsocket.send(b'0x50x00x00x00x00x00x00x00')
        except:
            print('Error: incomplete message')
        time.sleep(0.1)