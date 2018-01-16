import sys
import os
path1 = os.path.normpath(os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), os.pardir))
print(path1)
sys.path.append(path1)
import m_file 

data = {'host': 'aaa', 'port': 8009}
a = m_file.ini()

a.write('test1.json', data)

data_r = a.read('test1.json')
print(data_r)