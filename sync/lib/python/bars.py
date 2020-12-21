#!/usr/bin/python
import requests
import time
import sys
from math import isclose
from dbcon.postgres import Schema
from fin.utility import * 
from fin.fts import *

#get price bars: open, high, low, close, volume, dividends and splits
#2 times per month

def query_address(symbol, apikey, output_size, interval):
    #intervals: 1min, 5min, 15min, 30min, daily, weekly, monthly
    #output_size: full, compact
    if interval == 'daily':
        addr = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'
        addr += '&outputsize=' + output_size
    elif interval == 'weekly':
        addr = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED'
    elif interval == 'monthly':
        addr = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED'
    else:
        addr = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY'
        addr += '&outputsize=' + output_size
        addr += '&interval=' + interval
    addr += '&symbol=' + symbol
    addr += '&apikey=' + apikey
    return addr

def get_web_data(instrument_id, symbol, apikey='14QC5OD0TJP61MGS', output_size='full', interval='5min', sleep_time=12.1):
    page_addr = query_address(symbol, apikey, output_size, interval)
    try:
        contents = requests.get(page_addr)
    except:
        return None
    if contents is None:
        return None
    time.sleep(sleep_time)
    data = contents.json()
    key_time_series = None
    for key in data.keys():
        if 'Time Series' in key:
            key_time_series = key
    if not key_time_series in data or len(data[key_time_series]) == 0:
        return None 
    time_series = TimeSeries(instrument_id, interval)
    for dtime, bar_info in data[key_time_series].items():
        b_open = bar_info['1. open']
        b_high = bar_info['2. high']
        b_low = bar_info['3. low']
        b_close = bar_info['4. close']
        b_split_coeff = 1.0
        b_dividend = 0.0
        if len(bar_info) < 8:
            b_volume = bar_info['5. volume']
        else:
            b_volume = bar_info['6. volume']
            #b_adj_close = float(bar_info['5. adjusted close'])
            b_split_coeff = float(bar_info['8. split coefficient'])
            b_dividend = float(bar_info['7. dividend amount'])
        bar = Bar(dtime, b_open, b_high, b_low, b_close, b_volume)
        time_series.add(bar)
        if not isclose(b_split_coeff, 1.0, abs_tol=0.005):
            time_series.split_coeffs[bar.time] = b_split_coeff
        if not isclose(b_dividend, 0.0, abs_tol=0.001):
            time_series.dividends[bar.time] = b_dividend
    return time_series

def update_db_data_pulls(fin, instr_id, index_id, successful=True):
    cols = ['index_id', 'instrument_id', 'successful']
    insert_vals = [(index_id, instr_id, successful)]
    fin['data_pulls'].insert(cols, insert_vals)

if __name__ == "__main__":
    index_id = 1 #the intraday data index
    host = 'alphavantage' #the alphavantage host
    interval = '5min'
    output_size = 'full'
    
    if __debug__:
        fin = Schema(sch_name='fin', user_name='bk', host_name='kraken')
    else:
        fin = Schema(sch_name='fin', user_name='bk')
    npull = requests_remaining(fin, host)
    if len(sys.argv) > 1:
        args = [a.split('=') for a in sys.argv[1:]]
        args = {a[0]:a[1] for a in args}
        if 'max_pull' in args:
            npull = min(npull, int(args['max_pull']))
        if 'interval' in args:
            interval = args['interval']
        if 'index_id' in args:
            index_id = int(args['index_id'])
        if 'output_size' in args:
            output_size = args['output_size']

    host_id, day_lim, hour_lim, minute_lim = get_host_info(fin, host)
    sleep_time = 60. / minute_lim + 0.1
    fin['v_pulls_due'].select(conditions='index_id='+str(index_id))
    npull = min(npull, len(fin['v_pulls_due']['instrument_id'].values))
    pull_instr_ids = fin['v_pulls_due']['instrument_id'].values[:npull]
    fin['v_symbols'].select(conditions='host_id='+str(host_id))
    instr_id_symbols = dict(zip(fin['v_symbols']['instrument_id'].values, fin['v_symbols']['symbol'].values))
    npulled = 0
    for instr_id in pull_instr_ids:
        if not instr_id in instr_id_symbols:
            update_db_data_pulls(fin, instr_id, index_id, successful=False)
            continue
        symbol = instr_id_symbols[instr_id]
        time_series = get_web_data(instr_id, symbol, output_size=output_size, interval=interval, sleep_time=sleep_time)
        if time_series is None:
            print('id not found: ' + str(instr_id))
            update_db_data_pulls(fin, instr_id, index_id, successful=False)
            update_requests(fin, host)
            continue
        npulled += 1
        update_db_data_pulls(fin, instr_id, index_id)
        update_requests(fin, host)
        time_series.write()
        time_series.update_db(fin)
    print('job complete. Pulled ' + str(npulled))