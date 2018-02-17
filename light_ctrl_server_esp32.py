import network
import socket
import utime
import machine

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

def net_conn():
    ssid = 'vlmaba3'
    passwd = 'pricintorine1320'
    #ssid = 'vlmaba3'
    #passwd = ''

    sta_if = network.WLAN(network.STA_IF)
    print('network active: ', sta_if.active())
    sta_if.active(True)
    
    i=0
    while i<6 and sta_if.isconnected()==False:
        i += 1
        sta_if.connect(ssid, passwd)
        print(sta_if.isconnected(), "i: ", i)
        utime.sleep(1)
    print('is connected: ', sta_if.isconnected())
    if sta_if.isconnected() == True:
        psig.value(1)
    print('ifconfig: ', sta_if.ifconfig())
    return sta_if.ifconfig()[0]

sdata = socket_data()
duty0 = 10
duty1 = 10
pwm_freq = 5000
p0 = machine.PWM(machine.Pin(12), freq=pwm_freq)
p1 = machine.PWM(machine.Pin(14), freq=pwm_freq)
p0.duty(duty0*1024//100)
p1.duty(duty1*1024//100)
psig = machine.Pin(2, machine.Pin.OUT)
psig.value(0)
my_ip = net_conn()
print('my ip: ', my_ip)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind((my_ip, 8003))
serversocket.listen(5)

while True:     #main loop
    cmd1 = 0
    count = 0
    try:
        (clientsocket, address) = serversocket.accept()
    except OSError as err:
        #serversocket.close()
        print('restarting esp...')
        machine.reset()
        raise
        #serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #serversocket.bind((my_ip, 8003))
        #serversocket.listen(5)
    else:
        while (cmd1 != 5) and (count < 5): #count < 1: #(cmd1 != 5) and (count < 5):
            count += 1
            str1 = clientsocket.recv(32)
            print('count: ', count, 'str1: ', str1)
            try:
                a1 = sdata.deconstr(str1)
            except:
                print('Error: incomplete message')
            else:
                cmd1 = a1[0]
                chn = a1[1]
                duties = a1[2]
                print('str1: ', str1)
                print('a1: ', a1)
                print('cmd: ', cmd1)
                print('chn: ', chn)
                print('duties: ', duties)
                if cmd1 == 1:
                    str2 = sdata.constr(3, 0, [duty0, duty1, 0, 0])
                    clientsocket.send(str2) #b'0x30x00x00x00xff0xb20x7f0xdd')
                elif cmd1 == 2:
                    duty0 = duties[0]
                    duty1 = duties[1]
                    p0.duty(duty0*1024//100)
                    p1.duty(duty1*1024//100)
                    str2 = sdata.constr(3, 0, [duty0, duty1, 0, 0])    
                    clientsocket.send(str2) #b'0x30x00x00x00xdd0xb20x7f0xaa')
                elif cmd1 == 5:
                    print('success')
                    clientsocket.send(b'0x50x00x00x00x00x00x00x00')
        clientsocket.close()            #important to close connection even from server side
            #utime.sleep(0.1)
        