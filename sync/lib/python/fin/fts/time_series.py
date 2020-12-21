from .bar import Bar
from datetime import datetime, date, time
from os import listdir, makedirs
from os.path import join, exists
from copy import deepcopy

fts_data_dir = '/home/data/bk/fin/bars'

class TimeSeries:
    def __init__(self, instrument_id=None, interval='5min'):
        self.times_dict = {}
        self.times = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.instrument_id = instrument_id
        self.interval = interval
        self.dividends = {}
        self.split_coeffs = {}
    
    def read(self, mo_start=0, yr_start=0, mo_stop=13, yr_stop=9999, instrument_id=None):
        #stop month is included in the read 
        if instrument_id is None:
            instrument_id = self.instrument_id
            if instrument_id is None:
                return self
        else:
            self.instrument_id = instrument_id
        data_dir = join(fts_data_dir, self.interval, str(self.instrument_id)) 
        if not exists(data_dir):
            return self
        contents = listdir(data_dir)
        db_months = [(int(f[:4]), int(f[5:7])) for f in contents if '.csv' in f]
        db_months.sort()
        start = (yr_start, mo_start)
        stop = (yr_stop, mo_stop)
        db_files = [str(m[0]) + '-' + "{:02d}".format(m[1]) + '.csv' for m in db_months if m >= start and m <= stop]
        for fname in db_files:
            f = open(join(data_dir, fname),'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                fields = line.split(',')
                bar = Bar(fields[0], fields[1], fields[2], fields[3], fields[4], fields[5].strip())
                if not bar.time in self.times_dict:
                    self.add(bar)
        return self
    
    def write(self, mo_start=1, yr_start=1, mo_stop=12, yr_stop=9998, instrument_id=None):
        #stop month is included in the write
        if instrument_id is None:
            instrument_id = self.instrument_id
            if instrument_id is None:
                return self
        data_dir = join(fts_data_dir, self.interval, str(instrument_id)) 
        if not exists(data_dir):
            makedirs(data_dir)
        if len(self.times) == 0:
            return self
        start = min(self.times)
        if not isinstance(start, datetime):
            start = datetime.combine(start, time(0, 0, 0))
        start = max(start, datetime(yr_start, mo_start, 1))
        stop = max(self.times)
        if not isinstance(stop, datetime):
            stop = datetime.combine(stop, time(0, 0, 0))
        stop = min(stop, datetime(yr_stop, mo_stop, 1))
        self.read(start.month, start.year, stop.month, stop.year)
        self.sort()
        fname = str(start.year) + '-' + "{:02d}".format(start.month) + '.csv'
        f = open(join(data_dir, fname), 'w')
        prev_bar = self.__getitem__(0)
        f.write(str(prev_bar) + '\n')
        for i in range(1, len(self.times)):
            bar = self.__getitem__(i)
            if not bar.time.month == prev_bar.time.month or not bar.time.year == prev_bar.time.year:
                f.close()
                fname = str(bar.time.year) + '-' + "{:02d}".format(bar.time.month) + '.csv'
                f = open(join(data_dir, fname), 'w')
            f.write(str(bar) + '\n')
            prev_bar = deepcopy(bar)
        f.close()
        return self

    def sort(self):
        kvs = sorted(self.times_dict.items())
        self.times = [self.times[kv[1]] for kv in kvs]
        self.opens = [self.opens[kv[1]] for kv in kvs]
        self.highs = [self.highs[kv[1]] for kv in kvs]
        self.lows = [self.lows[kv[1]] for kv in kvs]
        self.closes = [self.closes[kv[1]] for kv in kvs]
        self.volumes = [self.volumes[kv[1]] for kv in kvs]
        self.times_dict = dict(zip(self.times, range(len(self.times)))) 
        return self

    def __getitem__(self, key):
        if isinstance(key, slice):
            ts = TimeSeries(self.instrument_id)
            start = key.start
            stop = key.stop
            step = key.step
            if isinstance(start, date):
                start = self.times_dict[start]
                if isinstance(stop, int):
                    stop += start
            if isinstance(stop, date):
                stop = self.times_dict[stop]
            slice_obj = slice(start,stop,step)
            ts.times = self.times[slice_obj]
            ts.opens = self.opens[slice_obj]
            ts.highs = self.highs[slice_obj]
            ts.lows = self.lows[slice_obj]
            ts.closes = self.closes[slice_obj]
            ts.volumes = self.volumes[slice_obj]
            for i in range(len(ts.times)):
                ts.times_dict[ts.times[i]] = i
            return ts
        if isinstance(key, date):
            key = self.times_dict[key]
        b = Bar(self.times[key], 
                self.opens[key], 
                self.highs[key], 
                self.lows[key], 
                self.closes[key], 
                self.volumes[key])
        return b
    
    def __setitem__(self, key, bar):
        if isinstance(key, date):
            if not key in self.times_dict:
                self.times_dict[bar.time] = len(self.times)
                self.times.append(bar.time)
                self.opens.append(bar.open)
                self.highs.append(bar.high)
                self.lows.append(bar.low)
                self.closes.append(bar.close)
                self.volumes.append(bar.volume)
                return
            key = self.times_dict[key]
        self.times[key] = bar.time
        self.opens[key] = bar.open
        self.highs[key] = bar.high
        self.lows[key] = bar.low
        self.volumes[key] = bar.volume
        return self
    
    def add(self, bar):
        self.__setitem__(bar.time, bar)
        return self

    def __len__(self):
        return len(self.times)
    
    def __contains__(self, key):
        return key in self.times_dict
    
    def index(self, time):
        return self.times_dict[time]
    
    def clear(self):
        self.times_dict.clear()
        self.times.clear()
        self.opens.clear()
        self.highs.clear()
        self.lows.clear()
        self.closes.clear()
        self.volumes.clear()
        return self
    
    def update_db(self, fin):
        def update_table(table, cols, vals_dict):
            table.select(conditions='instrument_id='+str(self.instrument_id))
            dates = set(table['date_of'].values)
            vals = []
            for d, val in vals_dict.items():
                if not d in dates:
                    vals.append( (self.instrument_id, d, val) )
            if len(vals) > 0:
                table.insert(cols, vals)
        cols = ['instrument_id', 'date_of', 'split_coeff']
        update_table(fin['stock_splits'], cols, self.split_coeffs)
        cols = ['instrument_id', 'date_of', 'dividend']
        update_table(fin['stock_dividends'], cols, self.dividends)
        return self
    
    def get_db_info(self, fin):
        table = fin['stock_splits']
        table.select(conditions='instrument_id='+str(self.instrument_id))
        self.split_coeffs = {table['date_of'][i]:table['split_coeff'][i] for i in range(len(table)) }
        table = fin['stock_dividends']
        table.select(conditions='instrument_id='+str(self.instrument_id))
        self.dividends = {table['date_of'][i]:table['dividend'][i] for i in range(len(table)) }
        return self