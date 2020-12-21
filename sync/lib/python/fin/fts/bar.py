from datetime import datetime, date

class Bar:

    _dt_format='%Y-%m-%d %H:%M:%S'
    _datetime_len = 17
    _date_len = 8
    
    def __init__(self, time, open, high, low, close, volume):
        self.time = None
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None

        if isinstance(time, datetime) or isinstance(time, date):
            self.time = time
        else:
            time_len = len(time) - 2
            self.time = datetime.strptime(time, self._dt_format[:time_len])
            date_only = time_len == 8
            if date_only:
                self.time = self.time.date()
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = int(volume)
    
    def __str__(self):
        time_len = self._date_len
        if isinstance(self.time, datetime):
            time_len = self._datetime_len
        s = datetime.strftime(self.time, self._dt_format[:time_len]) + ','
        s += "{0:.4f}".format(self.open) + ','
        s += "{0:.4f}".format(self.high) + ','
        s += "{0:.4f}".format(self.low) + ','
        s += "{0:.4f}".format(self.close) + ','
        s += str(self.volume)
        return s
    
    def __hash__(self):
        return hash(self.time)
    
    def __eq__(self, other):
        return self.time == other.time
    
    def __ne__(self, other):
        return not (self.time == other.time)

