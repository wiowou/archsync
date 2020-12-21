import os 

class Indicator(object):
    
    dataDir=os.path.expanduser('~/data/pmkt/ind/aoa/')
    
    def __init__(self,symbol):
        self.name = ''
        self.symbol = symbol
        self.bil = 0
        self.signal = []
        self.nmcap = []
        self.multipleLimit = 5.0
    
    def __add__(self,other):
        rv = Indicator(self.symbol)
        rv.bil = self.bil
        rv.signal = self.signal
        rv.nmcap = self.nmcap
        rv.multipleLimit = self.multipleLimit
        for i in range(0,len(self.signal)):
            rv.signal[i] += other.signal[i]
            rv.signal[i] = min(max(rv.signal[i],-1.0),1.0)
        return rv
    
    def write(self,fname):
        out = open(fname, 'w')
        out.write('Date          nmcap    signal\n')
        for i in range(0,len(self.signal)):
            dateStr = self.symbol.date[i].strftime('%d-%b-%y')
            nmcapStr = "{0:6.2f}".format(self.nmcap[i])
            sigStr = "{0:6.2f}".format(self.signal[i])
            out.write(dateStr + ',  ' + nmcapStr + ',  ' + sigStr + '\n')

from indicator.aoa import AoA
from indicator.multiple import Multiple
from indicator.account import Account
from indicator.symbol import Symbol