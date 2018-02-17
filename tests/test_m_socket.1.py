import sys
import os
import time
path1 = os.path.normpath(os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), os.pardir))
print(path1)
sys.path.append(path1)

import m_socket

s_data = m_socket.socket_data()
s_conn = m_socket.socket_connection()
s_conn.load_conf("c:\\Users\\pkrssak.DQI\\AppData\\Roaming\\lights_ctrl\\")
count = 0

while True:
    a = s_data.constr(2, 1, [10, 10, 10, 10])
    print("constructed str: ", a)
    status = s_conn.connect()
    print('connection status: ', status)
    s_conn.client_socket.send(a)
    recv1 = s_conn.client_socket.recv(32)
    print(count, '; received: ', recv1)
    s_conn.disconnect()
    time.sleep(0.1)
    count += 1