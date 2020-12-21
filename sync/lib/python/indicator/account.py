'''
Created on Feb 26, 2018

@author: 
'''
from indicator import Indicator

class Account:
    def __init__(self):
        self.vi = []
        self.secv = []
        self.maxRet = 1.0
        self.ret = 0.0
        self.sof = []
        self.sofh = []
        self.nmcap = []
        self.nbb = 0
        self._ind = Indicator('#none#')
    
    def PnL(self,ind):
        self._ind = ind
        self.nbb = 0
        self.sof = []
        sl = len(self._ind.signal)
        self.sofh = [[]]*sl
        self.vi = [0.0]*sl
        self.secv = [0.0]*sl
        self.nmcap = self._ind.nmcap
        self.maxRet = max(self.nmcap[self._ind.bil:]) / self.nmcap[self._ind.bil]
        self.vi[self._ind.bil] = 1.0
        for i in range(min(self._ind.bil+1,sl-1),sl):
            self.vi[i] = self.vi[i-1] * self.nmcap[i] / self.nmcap[i-1]
            isecv = 0.0
            if (self._ind.signal[i] < 0.0):
                isecv = max( self._ind.signal[i] * self.vi[i], -self.vi[i] )
                if (isecv < 0.0):
                    self.sof.append([self.nmcap[i],-isecv])
            elif (self._ind.signal[i] > 0.0):
                isecv = self._ind.signal[i] * self.secv[i-1]
                self.nbb += 1
            self.secv[i] = self.secv[i-1] - isecv
            self.vi[i] += isecv
            #self.buyBack(i)
            self.sofh[i] = self.sof
        self.ret = self.secv[sl-1]
        
    def buyBack(self,i):
        while ( len(self.sof) > 0 and self.nmcap[i] > self.sof[-1][0] and self.secv[i] > 0.0):
            self.nbb += 1
            sof = self.sof.pop()
            if (self.secv[i] - sof[1] < 1.0):
                sof[1] -= 1.0
            base = self.nmcap[i]
            if (self.vi[i] + sof[1] > 0.0):
                f1 = sof[1] / (self.vi[i] + sof[1])
                f2 = self.vi[i] / (self.vi[i] + sof[1])
            else:
                f1 = 0.0
                f2 = 1.0
            fact = f2 + f1 * sof[0] / base
            for mk in self.nmcap[i:]:
                mk *= fact
            self.vi[i] += sof[1]
            self.secv[i] -= sof[1]

    def write(self,fname):
        out = open(fname, 'w')
        out.write('Date          nmcap    signal   vi       secv\n')
        for i in range(0,len(self._ind.signal)):
            dateStr = self._ind.symbol.date[i].strftime('%d-%b-%y')
            nmcapStr = "{0:6.2f}".format(self.nmcap[i])
            sigStr = "{0:6.2f}".format(self._ind.signal[i])
            viStr = "{0:6.2f}".format(self.vi[i])
            secvStr = "{0:6.2f}".format(self.secv[i])
            out.write(dateStr + ',  ' + nmcapStr + ',  ' + sigStr + ',  ' + viStr + ',  ' + secvStr + '\n')
            