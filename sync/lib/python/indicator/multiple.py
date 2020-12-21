'''
Created on Feb 26, 2018

@author:
'''
from indicator import Indicator

class Multiple(Indicator):
    def __init__(self,symbol):
        Indicator.__init__(self, symbol)

        self.tpm = [0,5,500]
        self.tpf = [0,0.2,0.01]
#         for i in range(12,452,4):
#             self.tpm.append(i)
#             self.tpf.append(0.01)
        self.tpmLoc = 0
        
        '''
        self.tpm = [1.05,1.1,1.15,1.2,1.25,1.3]
        self.tpf = [0.0,0.1,0.1,0.1,0.1,0.1]
        for i in range(135,400,5):
            self.tpm.append(i/100.0)
            self.tpf.append(0.15)
        self.tpmLoc = 0
        '''
        
    def generateSignal(self):
        self.nmcap = []
        for mc in self.symbol.mktcap:
            self.nmcap.append(mc/self.symbol.mktcap[self.bil])
        self.signal = [0.0]*len(self.symbol.mktcap)
        self._advanceLoc(self.nmcap[self.bil])
        for i in range(self.bil,len(self.symbol.mktcap)):    
            if (self.nmcap[i] > self.tpm[self.tpmLoc]):
                self.signal[i] = -self._advanceLoc(self.nmcap[i])
    
    def _advanceLoc(self, inmcap):
        ntpf = 0.0
        while (self.tpm[self.tpmLoc] < inmcap):
            self.tpmLoc += 1
            ntpf += self.tpf[self.tpmLoc-1]
        ntpf = min(0.5,ntpf)
        return ntpf