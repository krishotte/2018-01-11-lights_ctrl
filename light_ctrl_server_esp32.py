import network
import socket
import utime
import machine
from m_file import uini
import uping

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

class socket_server:
    '''
    manages socket server
    provide ip address to set on init
    '''
    def __init__(self, ipaddr, conn):
        self.ipaddr = ipaddr
        self.sdata = socket_data()
        self.duty0 = 10
        self.duty1 = 10
        self.conn = conn 
        self.last_conn_check = 0  

    def start(self, timeout=None):
        '''
        starts socket server,
        waits for incomming connection for timeout (s) period
        '''
        self.timeout = timeout
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.serversocket.setblocking(False)
        self.serversocket.setblocking(True)
        self.serversocket.settimeout(timeout)
        print('binding server socket...')
        self.serversocket.bind((self.ipaddr, 8003))
        self.serversocket.listen(5)
        #self.listen()

    def close(self):
        '''
        closes socket server
        to begin again, run start method
        '''
        print('closing socket server')
        self.serversocket.close()

    def listen(self):
        '''
        waits for incomming connection for timeout (s) period
        '''
        print('listening ...')
        try:
            self.serversocket.accept()
        except OSError as err:
            if err.args[0] == 110:
                print('socket timeout')
            else:
                raise

    def listen_indef(self):
        '''
        waits for incoming connection in indefinite loop
        '''
        counter = 0
        while True:
            counter += 1
            print('counter: ', counter, ', listening...')
            #print('listening ...')
            self.check_comm()
            try:
                (self.clientsocket, self.clientaddress) = self.serversocket.accept()
            except OSError as err:
                if err.args[0] == 110:
                    print('socket timeout')
                else:
                    print(err)
                    raise
            else:
                print('message communicating...')
                self.exchange_comm()
                print('client socket closing...')
                self.clientsocket.close()

    def exchange_comm(self):
        cmd1 = 0
        count = 0
        while (cmd1 == 5) or (count < 2): #count < 1: #(cmd1 != 5) and (count < 5):
            count += 1
            str1 = self.clientsocket.recv(32)
            print('count: ', count, 'str1: ', str1)
            try:
                a1 = self.sdata.deconstr(str1)
            except:
                print('Error: incomplete message')
            else:
                cmd1 = a1[0]
                chn = a1[1]
                duties = a1[2]
                '''
                print('str1: ', str1)
                print('a1: ', a1)
                print('cmd: ', cmd1)
                print('chn: ', chn)
                print('duties: ', duties)
                '''
                print('cmd: ', cmd1, ' , chn: ', chn, ' , duties: ', duties)
                if cmd1 == 1:
                    str2 = self.sdata.constr(3, 0, [self.duty0, self.duty1, 0, 0])
                    self.clientsocket.send(str2) #b'0x30x00x00x00xff0xb20x7f0xdd')
                elif cmd1 == 2:
                    self.duty0 = duties[0]
                    self.duty1 = duties[1]
                    p0.duty(self.duty0*1023//100)
                    p1.duty(self.duty1*1023//100)
                    str2 = self.sdata.constr(3, 0, [self.duty0, self.duty1, 0, 0])    
                    self.clientsocket.send(str2) #b'0x30x00x00x00xdd0xb20x7f0xaa')
                elif cmd1 == 5:
                    print('success')
                    self.clientsocket.send(b'0x50x00x00x00x00x00x00x00')
    
    def check_comm(self):
        actual_time = utime.time()
        if (actual_time - self.last_conn_check) > self.timeout*5:
            print('checking network connection')
            self.last_conn_check = actual_time
            connected = self.conn.check_conn()
            if connected == False:
                #what about running socket connection?
                #will it still be running after network restart?
                self.close()
                print('closing network connection')
                self.conn.close()
                print('establishing network connection...')
                #TODO not tested
                self.conn.connect2()
                self.start()
                self.listen_indef()

class network_conn:
    '''
    manages network connectivity
    provide configuration file name on init
    '''
    def __init__(self, config_file):
        self.sta_if = network.WLAN(network.STA_IF)
        print('network is active: ', self.sta_if.active())
        self.sta_if.active(True)
        self.ini = uini()
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        self.conf = self.ini.read(self.config_file)
        try:
            self.ssid = self.conf['ssid']
        except KeyError:
            self.ssid = ''
        try:
            self.passwd = self.conf['passwd']
        except:
            self.passwd = ''
        try:
            self.ipaddr = self.conf['ipaddr']
        except:
            self.ipaddr = ''
        try:
            self.gateway = self.conf['gateway']
        except:
            self.gateway = ''
        print('loaded config: ssid: ', self.ssid, ' passwd: ', self.passwd, ' ip address: ', self.ipaddr, ' gateway: ', self.gateway)

    def connect(self):
        '''
        connects to AP
        assigns provided ip address to server
        '''
        i = 0
        while i<6 and self.sta_if.isconnected()==False:
            i += 1
            self.sta_if.connect(self.ssid, self.passwd)
            print('connecting... ', self.sta_if.isconnected(), ", stage: ", i)
            utime.sleep(3)
        print('is connected?: ', self.sta_if.isconnected())
        if self.sta_if.isconnected() == True:
            self.sta_if.ifconfig((self.ipaddr,'255.255.255.0','192.168.0.1','192.168.0.1'))
            psig.duty(10) 
        else:
            psig.duty(0)
        print('ifconfig: ', self.sta_if.ifconfig())
        #return sta_if.ifconfig()[0]

    def connect2(self):
        '''
        improved preffered connect method
        '''
        self.sta_if.ifconfig((self.ipaddr,'255.255.255.0', self.gateway, self.gateway))
        self.sta_if.connect(self.ssid, self.passwd)
        utime.sleep(5)
        print('is connected? (sta_if): ', self.sta_if.isconnected())
        print('ifconfig: ', self.sta_if.ifconfig())
        check_conn = self.check_conn()
        print('network connected: ', check_conn)
        if check_conn == True:
            psig.duty(10)
        else:
            psig.duty(0)

    def check_conn(self):
        print('is connected? (sta_if): ', self.sta_if.isconnected)
        try:
            ping_status = uping.ping(self.gateway)
            if ping_status == (4, 4):
                conn_status = True
                print('ping: connected')
            else:
                conn_status = True
                print('ping: some packets lost')
        except OSError:
            print('ping: not connected')
            conn_status = False
        return conn_status

    def close(self):
        print('disconnecting network...')
        self.sta_if.disconnect()
        print('network connected: ', self.check_conn())
        psig.duty(0)

#global variables:
pwm_freq = 5000
psig = machine.PWM(machine.Pin(2), freq=pwm_freq)
psig.duty(100)
p0 = machine.PWM(machine.Pin(12), freq=pwm_freq)
p1 = machine.PWM(machine.Pin(14), freq=pwm_freq)
p0.duty(10*1023//100)
p1.duty(10*1023//100)
    

def net_conn():
    """
    connect to network function
    """
    #ssid = 'vlmaba3'
    #passwd = 'pricintorine1320'
    ssid = "UPC5515895"
    passwd = "hsa8de6yrxGh"

    sta_if = network.WLAN(network.STA_IF)
    print('network active: ', sta_if.active())
    sta_if.active(True)
    
    i=0
    while i<6 and sta_if.isconnected()==False:
        i += 1
        sta_if.connect(ssid, passwd)
        print(sta_if.isconnected(), "i: ", i)
        utime.sleep(2)
    print('is connected: ', sta_if.isconnected())
    if sta_if.isconnected() == True:
        psig.value(1)
    print('ifconfig: ', sta_if.ifconfig())
    return sta_if.ifconfig()[0]

def net_conn2(ipaddr):
    """
    connect to network function
    """
    #ssid = 'vlmaba3'
    #passwd = 'pricintorine1320'
    #ssid = "UPC5515895"
    #passwd = "hsa8de6yrxGh"
    ssid = "AndroidPK"
    passwd = "alfa1234"
    
    sta_if = network.WLAN(network.STA_IF)
    print('network active: ', sta_if.active())
    sta_if.active(True)
    #sta_if.ifconfig(('192.168.0.9','255.255.255.0','192.168.0.1','192.168.0.1'))
    
    i=0
    while i<6 and sta_if.isconnected()==False:
        i += 1
        sta_if.connect(ssid, passwd)
        print(sta_if.isconnected(), "i: ", i)
        utime.sleep(3)
    print('is connected: ', sta_if.isconnected())
    if sta_if.isconnected() == True:
        sta_if.ifconfig((ipaddr,'255.255.255.0','192.168.0.1','192.168.0.1'))
        psig.duty(10) #value(1)
    else:
        psig.duty(0)
    print('ifconfig: ', sta_if.ifconfig())
    return sta_if.ifconfig()[0]

def main():
    'runs main script'
    global conn
    conn = network_conn('conf.json')
    conn.connect2()
    global server1
    server1 = socket_server(conn.ipaddr, conn)
    server1.start(20)
    server1.listen_indef()

def main_old(ipaddr):
    'runs former main script version'
    sdata = socket_data()
    duty0 = 10
    duty1 = 10
    pwm_freq = 5000
    p0 = machine.PWM(machine.Pin(12), freq=pwm_freq)
    p1 = machine.PWM(machine.Pin(14), freq=pwm_freq)
    p0.duty(duty0*1023//100)
    p1.duty(duty1*1023//100)
    #psig = machine.Pin(2, machine.Pin.OUT)
    #psig.value(0)
    global psig
    psig = machine.PWM(machine.Pin(2), freq=pwm_freq)
    psig.duty(100)
    my_ip = net_conn2(ipaddr)
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
                        p0.duty(duty0*1023//100)
                        p1.duty(duty1*1023//100)
                        str2 = sdata.constr(3, 0, [duty0, duty1, 0, 0])    
                        clientsocket.send(str2) #b'0x30x00x00x00xdd0xb20x7f0xaa')
                    elif cmd1 == 5:
                        print('success')
                        clientsocket.send(b'0x50x00x00x00x00x00x00x00')
            clientsocket.close()            #important to close connection even from server side
                #utime.sleep(0.1)

#main_old()         