# socket communication speed tester

import time
from m_socket import socket_data, socket_connection
import socket

s_data = socket_data()
s_conn = socket_connection()

time_start = time.clock()

for i in range(1):
    for j in range(100):
        s_conn.ip = '192.168.0.9'
        s_conn.port = 8003
        status = s_conn.connect()

        if status:
            sockstr = s_data.constr(2, 1, [j, j, 0, 0])
            s_conn.client_socket.send(sockstr)
            recv1 = s_conn.client_socket.recv(32)
            curr_setup = s_data.deconstr(recv1)

        s_conn.disconnect()

time_stop = time.clock()

print(' test took: ', time_stop - time_start, ' seconds')
