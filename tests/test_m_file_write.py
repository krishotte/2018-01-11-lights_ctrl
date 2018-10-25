import sys
import os
path1 = os.path.normpath(os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), os.pardir))
print("appended path: " + path1)
sys.path.append(path1)
import m_file 

path2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.ini')
print('file path: ' + path2)


"""data = {'host': 'aaab', 'port': 8009}
a = m_file.ini()

a.write('test1.json', data)
data_r = a.read('test2.json')
print(data_r)
"""

a = m_file.ini()

ch1_val = [100, 70, 50, 40, 10]
ch2_val = [90, 70, 60, 42, 0]
data = {
    'ch1_val': ch1_val,
    'ch2_val': ch2_val
}

a.write('settings01.json', data)
