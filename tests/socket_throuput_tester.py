import socket
import time



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

time_start = time.clock()

for i in range(1000):
    strdata = str(hex(i//10)).encode() + str(hex(0)).encode() + str(hex(0)).encode() + str(hex(0)).encode()
    # self.strdata = self.strdata + str(hex(pwm)).encode()
    # print('i: ', i)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(4)
    client_socket.connect(('192.168.0.9', 8003))
    client_socket.send(strdata)
    client_socket.recv(16)
    client_socket.close()

time_stop = time.clock()
print(' test took: ', time_stop - time_start, ' seconds')
