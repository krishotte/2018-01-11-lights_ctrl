"""
collects logs and provides log output
into file, label widget, etc.
"""
class log:
    def __init__(self, maxlines):
        self.strg = ''
        self.max_lines = maxlines
        self.line_count = 0
    def addline(self, line):
        'adds line to log'
        if len(self.strg) != 0:
            self.strg_list = self.strg.split('\n')
            self.line_count = len(self.strg_list)
        #print('line_count = ', self.line_count)
        if self.line_count < self.max_lines:
            if self.line_count != 0:
                self.strg += '\n'
            self.strg += line
        else:
            self.strg_list.pop(0)
            #print('newlength = ', len(self.strg_list))
            self.strg = ''
            for str1 in self.strg_list:
                self.strg += str1
                self.strg += '\n'
            self.strg += line
        return self.strg
        #print('strg_list: ', self.strg_list)
        #print('strg: ', self.strg)
        #print('----------------------')