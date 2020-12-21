
from datetime import datetime

class Symbol:
    def __init__(self,name=''):
        self.name = name
        self.mktcap = []
        self.date = []
        
    def readMcap(self,fname):
        self.mktcap = []
        with open(fname, 'r') as f:
            for line in f:
                self.mktcap.append(float(line))
    
    def readDate(self,fname):
        self.date = []
        with open(fname, 'r') as f:
            for line in f:
                line = line.strip()
                d = datetime.strptime(line,'%d-%b-%y')
                self.date.append(d)
        