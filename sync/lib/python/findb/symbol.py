from datetime import datetime
from .ohlc import OHLC
import os

class Symbol(object):

    dataDir=os.path.expanduser('~/data/mkt/price/')
    
    def __init__(self,name=''):
        self.name=name
        self.ohlc = {}
        self.date = []
        self.open = []
        self.high = []
        self.low = []
        self.close = []
        self.mktcap = []
        self.volume = []
    
    def read(self):
        fname = os.path.join(self.dataDir,self.name+'.csv')
        if os.path.exists(fname):
            f = open(fname,'r')
            line = f.readline() #read header
            for line in f:
                ohlc=OHLC()
                dt,op,high,low,close,volume,mktcap=line.split(',')
                dt=datetime.strptime(dt,'%d-%b-%y')
                ohlc.open=float(op)
                ohlc.high=float(high)
                ohlc.low=float(low)
                ohlc.close=float(close)
                ohlc.volume=float(volume)
                ohlc.mktcap=float(mktcap)
                self.ohlc[dt.date()]=ohlc
                self.date.append(dt)
                self.open.append(ohlc.open)
                self.high.append(ohlc.high)
                self.low.append(ohlc.low)
                self.close.append(ohlc.close)
                self.mktcap.append(ohlc.mktcap)
                self.volume.append(ohlc.volume)
            f.close()
    
    def write(self):
        if (not os.path.exists(self.dataDir)):
            os.makedirs(self.dataDir)
        fname = os.path.join(self.dataDir,self.name+'.csv')
        f = open(fname,'w')
        f.write('date,open,high,low,close,volume,mktcap\n')
        for k,v in sorted(self.ohlc.items()):
            f.write(datetime.strftime(k,'%d-%b-%y')+','+str(v)+'\n')
        f.close()
            
        