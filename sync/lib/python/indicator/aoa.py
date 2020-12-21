import numpy as np
from scipy import stats
import math
import os

from indicator import Indicator

class AoA(Indicator):
    
    def __init__(self,symbol):
        Indicator.__init__(self, symbol)
        self.name = 'aoa'
        self.trendPer = 5
        self.trendPerBrat = 15
        self.slr = 0.7 #price ratio that you cut losses and sell
        self.bir = 1.0 #price ratio that you buy back in after a sell
        self.frat = 0.4 #the ratio brat is allowed to fall in a day to trigger sell
        self.slope = []
        self.angle = []
        self.brat = [] #ratio of buy slope to sell slope sum over last trendPerBrat
        self._bip = 0.0

    def generateSignal(self):
        self.nmcap = []
        if (self.symbol.close[self.bil] > 0.0):
            self._bip = self.symbol.close[self.bil]
            for mc in self.symbol.close:
                self.nmcap.append(mc/self.symbol.close[self.bil])
        elif (self.symbol.mktcap[self.bil] > 0.0):
            self._bip = self.symbol.mktcap[self.bil]
            for mc in self.symbol.mktcap:
                self.nmcap.append(mc/self.symbol.mktcap[self.bil])
        elif (self.symbol.open[self.bil] > 0.0):
            self._bip = self.symbol.open[self.bil]
            for mc in self.symbol.open:
                self.nmcap.append(mc/self.symbol.open[self.bil])
        self._angleHistory()
        self.signal = [0]*len(self.brat)
        bullSell = False
        sp = 0.0
        bp = self.nmcap[self.bil]
        stopLoss = False
        for i in range(1,len(self.brat)):
            if (self.nmcap[i] < self.multipleLimit or i <= self.trendPerBrat or math.isinf(self.brat[i-1]) or self.brat[i-2] < 1e-8):
                continue
            if (math.isinf(self.brat[i]) or (self.brat[i-1]/self.brat[i-2] < self.frat and self.brat[i] < self.brat[i-1]) ):
                bullSell = True
                self.signal[i] = -1.0
                sp = max(self.nmcap[i],sp)
            elif (bullSell and self.brat[i] > self.brat[i-1]):
            #    self.signal[i] = 1.0
                bullSell = False
            elif (self.brat[i] < 1.0 and self.brat[i-1] > 1.0):
                self.signal[i] = -1.0
            elif (bp > 0.0 and self.nmcap[i]/bp < self.slr):
                self.signal[i] = -1.0
                bp = 0.0
                sp = max(self.nmcap[i],sp)
                stopLoss = True
            elif (self.brat[i] > 1.0 and self.brat[i-1] < 1.0):
                self.signal[i] = 1.0
            elif (sp > 0.0 and self.nmcap[i]/sp > self.bir and not stopLoss):
                self.signal[i] = 1.0
                bp = self.nmcap[i]
                sp = 0.0
            pass
    
    def _angleHistory(self):
        self.angle = []
        self.slope = []
        for i in range(0,len(self.symbol.mktcap)):
            if (i < self.trendPer):
                self.slope.append(0.0)
                self.angle.append(0.0)
                self.brat.append(0.0)
            else:
                slope, angle = self._angleAtTime(i)
                self.slope.append(slope)
                self.angle.append(angle)
                if (i < self.trendPerBrat):
                    self.brat.append(0.0)
                else:
                    num = sum(s for s in self.slope[-self.trendPerBrat:] if s > 0)
                    den = -sum(s for s in self.slope[-self.trendPerBrat:] if s < 0)
                    if (den < 1e-8):
                        self.brat.append(float('inf'))
                    else:
                        self.brat.append(num/den)
    
    def _angleAtTime(self,time):
        y = np.asarray(self.symbol.mktcap[ max(time-self.trendPer+1,0) : time+1 ])
        y /= self._bip
        x = np.linspace(0.0,self.trendPer-1.0,self.trendPer)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        angle = math.atan2(slope,1.0) * 180.0 / math.pi
        return slope, angle

    def write(self,fname=''):
        if (not os.path.exists(self.dataDir)):
            os.makedirs(self.dataDir)
        if (fname == '' ):
            fname = os.path.join(self.dataDir,self.symbol.name+'.csv')
        out = open(fname, 'w')
        out.write('Date,         nmcap,   signal,   brat\n')
        for i in range(0,len(self.signal)):
            dateStr = self.symbol.date[i].strftime('%d-%b-%y')
            nmcapStr = "{0:6.2f}".format(self.nmcap[i])
            sigStr = "{0:6.2f}".format(self.signal[i])
            bratStr = "{0:6.1f}".format(self.brat[i])
            if (math.isinf(self.brat[i]) ):
                bratStr = '   inf'
            out.write(dateStr + ',  ' + nmcapStr + ',  ' + sigStr + ',  ' + bratStr + '\n')
