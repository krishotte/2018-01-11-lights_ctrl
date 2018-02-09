import sys
import os
path1 = os.path.normpath(os.path.join(os.path.join(os.path.abspath(__file__), os.pardir), os.pardir))
print(path1)
sys.path.append(path1)

import m_logger

log1 = m_logger.log(7)

for i in range(23):
    str1 = 'a' + str(i)
    str1 = log1.addline(str1)
    print(str1)
    print('-----------------------')

