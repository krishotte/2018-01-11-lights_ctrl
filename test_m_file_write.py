import m_file 

data = {'host': 'aaa', 'port': 8009}
a = m_file.ini()

a.write('test1.json', data)

data_r = a.read('test1.json')
print(data_r)