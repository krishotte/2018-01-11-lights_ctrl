import sys
import os
path1 = os.path.normpath(os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), os.pardir))
print(path1)
sys.path.append(path1)

import m_socket

s_data = m_socket.socket_data()

duties = [100,70,50,0]
print("duties to send: ", duties)
a = s_data.constr(2, 1, duties)
print("constructed str: ", a)

duties_back = s_data.deconstr(a)
print("deconstructed duties: ", duties_back[2])
print("pwms: ", s_data.pwms)

if duties_back[2] == duties:
    print("constr, deconstr success")
print('-------------------------------')

s_conn = m_socket.socket_connection()
s_conn.load_conf(path1)
print('connecting...')
status = s_conn.connect()
print('connection status: ', status)