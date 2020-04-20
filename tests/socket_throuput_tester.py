import socket
import time

import sys
from os import path

dir1 = path.dirname(path.realpath(__file__))
print('parent dir: ', dir1)
sys.path.append(dir1)

from m_socket import socket_data

"""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(4)
client_socket.connect(('192.168.0.9', 8003))

time_start = time.clock()

for i in range(1000):
    strdata = str(hex(i//10)).encode() + str(hex(0)).encode() + str(hex(0)).encode() + str(hex(0)).encode()
    # self.strdata = self.strdata + str(hex(pwm)).encode()
    client_socket.send(strdata)
    client_socket.recv(16)
    
time_stop = time.clock()
print(' test took: ', time_stop - time_start, ' seconds')

client_socket.close()
"""

data = socket_data()

time_start = time.clock()



for i in range(100):
    strdata = data.constr(2, 0, [i, 0, 0, 0])
    # self.strdata = self.strdata + str(hex(pwm)).encode()
    # print('i: ', i)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10)
    client_socket.connect(('192.168.0.9', 8003))
    client_socket.send(strdata)
    print(client_socket.recv(32))
    client_socket.close()

time_stop = time.clock()
print(' test took: ', time_stop - time_start, ' seconds')
