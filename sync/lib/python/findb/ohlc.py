class OHLC(object):
    def __init__(self):
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0.0
        self.mktcap = 0.0
    
    def __str__(self):
        s = str(self.open) + ','
        s += str(self.high) + ','
        s += str(self.low) + ','
        s += str(self.close) + ','
        s += str(self.volume) + ','
        s += str(self.mktcap)
        return s