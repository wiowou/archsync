#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from dbcon.postgres import Schema
from fin.utility import * 
from fin.match_utility import * 

import os
import json

#attempt to automatically create ties between symbols and obtain new symbols
#not scheduled

def get_simfin_stats(fin, sim_ids, years=[], TTM=True, get_indicator_ids=None):
    #nine years, including TTM max per company in this call
    #years with no data will just return 0's and a closing price
    #each company's data is seperate element in array
    if len(years) + int(TTM) > 9 or len(years) + int(TTM) < 1:
        return None
    fin['simfin_indicators'].select()
    indicator_ids = fin['simfin_indicators']['id'].values
    indicator_names = fin['simfin_indicators']['name'].values
    indicator_id_to_name = dict(zip(indicator_ids, indicator_names))
    if get_indicator_ids is None:
        get_indicator_ids = indicator_ids
    
    sim_ids = [int(i) for i in sim_ids]
    json_data = {'search':[], 'simIdList':sim_ids, 'resultsPerPage':0}
    for year in years:
        meta = []
        meta.append({"id": 6, "value": "fy", "operator": "eq"})
        meta.append({"id": 7, "value": year, "operator": "eq"})
        for i_id in get_indicator_ids:
            json_data['search'].append( {'indicatorId':i_id, 'meta':meta} )
    if TTM:
        meta = []
        meta.append({"id": 6, "value": "TTM", "operator": "eq"})
        for i_id in get_indicator_ids:
            json_data['search'].append( {'indicatorId':i_id, 'meta':meta} )
    try:
        update_requests(fin, 'simfin')
        r = requests.post('https://simfin.com/api/v1/finder?api-key=' + 'uQmMhU3npviy0DEptnscYIGljcbSjECF', json=json_data)
    except:
        return None
    if r is None:
        return None
    data = r.json()
    year_periods = []
    for year in years:
        year_periods.append( (year, 'fy') )
    if TTM:
        year_periods.append('ttm')
    ret = {}
    for result in data['results']:
        simId = result['simId']
        ret[simId] = {}
        for year in years:
            ret[simId][(year, 'fy')] = {}
        if TTM:
            ret[simId]['ttm'] = {}
        i = 0
        for val in result['values']:
            if i % len(indicator_ids) == 0:
                year_period = year_periods[i // len(indicator_ids)]
                ret[simId][year_period] = {}
            iid = val['indicatorId']
            iid_name = indicator_id_to_name[iid]
            ret[simId][year_period][iid_name] = val['value']
            i += 1
    return ret

def get_alphavantage_data(name, symbol=None, sleep_time=12.1):
    base_addr = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords='
    apikey = '14QC5OD0TJP61MGS'
    ret = {'symbol':symbol, 'name':None, 'quote':None, 'request_count':0}
    if not symbol is None:
        page_addr = base_addr + symbol + '&apikey=' + apikey
        try:
            contents = requests.get(page_addr)
            ret['request_count'] += 1
        except:
            return ret
        if contents is None:
            return ret
        time.sleep(sleep_time)
        data = contents.json()
        if not 'bestMatches' in data or len(data['bestMatches']) == 0:
            return ret 
        for s in data['bestMatches']:
            if s['1. symbol'] == symbol:
                ret['name'] = simplify_instrument_name(s['2. name'])
                quote = get_alphavantage_quote(symbol=symbol)
                ret['request_count'] += 1
                i = 0
                while quote is None and i < 3:
                    quote = get_alphavantage_quote(symbol=symbol)
                    ret['request_count'] += 1
                    i += 1
                if not quote is None:
                    ret['quote'] = quote['last']
                else:
                    ret['name'] = None
                    ret['symbol'] = None
                return ret 
    keywords = name.replace(' ', '%20')
    page_addr = base_addr + keywords + '&apikey=' + apikey
    try:
        contents = requests.get(page_addr)
        ret['request_count'] += 1
    except:
        return ret 
    if contents is None:
        return ret 
    time.sleep(sleep_time)
    data = contents.json()
    if not 'bestMatches' in data or len(data['bestMatches']) == 0:
        return ret 
    score_sy_name = [ (float(s['9. matchScore']), s['1. symbol'], s['2. name']) for s in data['bestMatches']]
    best_match = max(score_sy_name)
    ret['symbol'] = best_match[1]
    ret['name'] = simplify_instrument_name(best_match[2])
    quote = get_alphavantage_quote(symbol=ret['symbol'])
    ret['request_count'] += 1
    i = 0
    while quote is None and i < 3:
        quote = get_alphavantage_quote(symbol=ret['symbol'])
        ret['request_count'] += 1
        i += 1
    if not quote is None:
        ret['quote'] = quote['last']
    else:
        ret['name'] = None
        ret['symbol'] = None
    return ret

def get_match_stocks_data(fin, max_req=500, clear_match_stocks=False):
    #get all simfin ids, symbols, names
    #throw out all n/a symbols
    #throw out all existing simfin ids
    #check remaining ids for active quote on marketwatch, throw out any without active quote
    if clear_match_stocks:
        fin['match_stocks'].delete()
    fin['simfin_entities'].select()
    db_simfin_ids = set(fin['simfin_entities']['sim_id'].values)
    nreq = min(max_req, requests_remaining(fin, 'alphavantage'))

    simfin_root = 'https://simfin.com/api/v1'
    all_entities = '/info/all-entities?api-key=' + 'uQmMhU3npviy0DEptnscYIGljcbSjECF'
    page_addr = simfin_root + all_entities
    try:
        update_requests(fin, 'simfin')
        contents = requests.get(page_addr)
    except:
        return None
    if contents is None:
        return None
    entities = contents.json()
    sim_ids = []
    for et in entities:
        sim_ids.append(et['simId'])
    sim_stats = get_simfin_stats(fin, sim_ids=sim_ids, get_indicator_ids=['0-71', '0-31', '4-11'])
    if sim_stats is None:
        return None
    ireq = 0
    for et in entities:
        if ireq >= nreq:
            break
        sim_id = et['simId']
        if sim_id in db_simfin_ids:
            continue
        fin['simfin_entities'].insert(['sim_id'], [(sim_id,)])
        if not isinstance(et['name'], str):
            continue
        name = simplify_instrument_name(et['name'])
        if not isinstance(et['ticker'], str):
            continue
        ticker = et['ticker'].upper().strip()
        if ticker == 'N/A':
            continue
        marketwatch_quote = get_marketwatch_quote(ticker)
        if marketwatch_quote is None and (ticker[-1] == 'A' or ticker[-1] == 'B'):
            ticker = ticker[:-1] + '.' + ticker[-1]
            marketwatch_quote = get_marketwatch_quote(ticker)
        if marketwatch_quote is None:
            continue
        if not marketwatch_quote['currency'] == 'USD':
            continue
        if not sim_id in sim_stats:
            continue
        row = Match()
        row.sim_id = sim_id
        row.sim_symbol = ticker
        row.mw_symbol = ticker
        row.sim_name = name
        row.sim_quote = sim_stats[sim_id]['ttm']['last_closing_price']
        row.sim_mktcap = sim_stats[sim_id]['ttm']['market_capitalization']
        row.mw_name = marketwatch_quote['name']
        if not row.mw_name is None:
            row.mw_name_match_score = name_match_score(row.sim_name, row.mw_name)
        row.mw_quote = marketwatch_quote['quote']
        row.mw_mktcap = marketwatch_quote['mkt_cap']
        alpha_data = get_alphavantage_data(row.sim_name, row.sim_symbol)
        ireq += alpha_data['request_count'] 
        update_requests(fin, 2, alpha_data['request_count'])
        if alpha_data['quote'] is None:
            continue
        row.alpha_name = alpha_data['name']
        row.alpha_symbol = alpha_data['symbol']
        row.alpha_quote = alpha_data['quote']
        if not row.alpha_name is None:
            row.alpha_name_match_score = name_match_score(row.sim_name, row.alpha_name)
        if row.alpha_name_match_score is None or row.mw_name_match_score is None or row.alpha_name_match_score < 0.8 or row.mw_name_match_score < 0.8:
            if row.alpha_symbol == row.sim_symbol and row.sim_symbol == row.mw_symbol and not row.sim_quote is None:
                min_quote = min(row.alpha_quote, row.mw_quote, row.sim_quote)
                max_delta = max( abs(row.alpha_quote - row.sim_quote), abs(row.sim_quote - row.mw_quote), abs(row.mw_quote - row.alpha_quote) )
                if max_delta / min_quote < 0.1:
                    row.sim_name = row.mw_name
                    row.alpha_name = row.mw_name
                    row.mw_name_match_score = 1.0
                    row.alpha_name_match_score = 1.0
                    #replace next line with getting list of available statements to statement pulls, adding an instrument id and adding to symbols table
                    add_stock(fin, row)
                    #fin['match_stocks'].insert(row.cols(), [row.to_tuple()])
        elif row.mw_name_match_score >= 0.8 and row.alpha_name_match_score >= 0.8:
            #replace next line with getting list of available statements to statement pulls, adding an instrument id and adding to symbols table
            add_stock(fin, row)
            #fin['match_stocks'].insert(row.cols(), [row.to_tuple()])

if __name__ == "__main__":
    if __debug__:
        fin = Schema(sch_name='fin', user_name='bk', host_name='kraken')
    else:
        fin = Schema(sch_name='fin', user_name='bk')
    max_req = min(requests_remaining(fin, host=2), requests_remaining(fin, host=3), requests_remaining(fin, host=4))
    get_match_stocks_data(fin, max_req=max_req)
    print('job complete.')
    pass