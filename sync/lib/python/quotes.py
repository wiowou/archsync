#!/usr/bin/python
import sys
from datetime import datetime
from dbcon.postgres import Schema
from fin.utility import *

#price, marketcap, P/E, and dividend yield info
#daily

instrument_ids = []
quotes = []
pe_ratios = []
mkt_caps = []
div_yields = []
successfuls = []

def get_stock_quotes(ntotal, pull_symbols):
    npulled = 0
    for i in range(ntotal):
        result = get_marketwatch_quote(symbol=pull_symbols[i])
        if result is None:
            successfuls.append(False)
            continue
        successfuls.append(True)
        instrument_ids.append(pull_instr_ids[i])
        quotes.append(result['quote'])
        pe_ratios.append(result['pe_ratio'])
        mkt_caps.append(result['mkt_cap'])
        div_yields.append(result['div_yield'])
        npulled += 1
    return npulled

def get_treasury_quote(pull_instr_ids, pull_symbols):
    npulled = 0
    root_page_addr = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'
    page_addr = root_page_addr 
    try:
        page = requests.get(page_addr)
    except:
        return npulled
    soup = BeautifulSoup(page.text,'html.parser')
    try:
        table_tag = soup.find('table', {'class' : 't-chart'})
        tags = table_tag.find_all('tr')
    except:
        return npulled
    headers = []
    for tag in tags[0]:
        headers.append(tag.text)
    yields = []
    for tag in tags[-1]:
        yields.append(tag.text)
    headers = [h.lower().strip() for h in headers[1:]]
    yields = [float(y)/100. for y in yields[1:]]
    headers_to_yields = dict(zip(headers, yields))
    for i in range(len(pull_instr_ids)):
        symbol = pull_symbols[i]
        if not symbol in headers_to_yields:
            continue
        successfuls.append(True)
        instrument_ids.append(pull_instr_ids[i])
        quotes.append(headers_to_yields[symbol])
        pe_ratios.append(None)
        mkt_caps.append(None)
        div_yields.append(headers_to_yields[symbol])
        npulled += 1
    return npulled

def get_cpi_quote(pull_instr_ids, pull_symbols):
    npulled = 0
    root_page_addr = 'https://www.bls.gov/charts/consumer-price-index/consumer-price-index-by-category.htm'
    page_addr = root_page_addr 
    table_id = 'cpi_rc_1cpibycat'
    try:
        page = requests.get(page_addr)
    except:
        return npulled
    soup = BeautifulSoup(page.text,'html.parser')
    try:
        table_tag = soup.find('table', {'id' : table_id})
    except:
        return npulled
    for i in range(len(pull_instr_ids)):
        search_id = table_id + pull_symbols[i]
        tag = table_tag.find('th', {'id' : search_id})
        tag = tag.find_next_sibling('td')
        yld = float(tag.text.replace('%', '').strip()) / 100.
        successfuls.append(True)
        instrument_ids.append(pull_instr_ids[i])
        quotes.append(yld)
        pe_ratios.append(None)
        mkt_caps.append(None)
        div_yields.append(yld)
        npulled += 1
    return npulled

#doesn't work
def get_gdp_quote(pull_instr_ids, pull_symbols):
    npulled = 0
    root_page_addr = 'https://apps.bea.gov/iTable/iTable.cfm?reqid=19&step=3&isuri=1&nipa_table_list=5&categories=survey'
    page_addr = root_page_addr 
    try:
        page = requests.get(page_addr)
    except:
        return npulled
    soup = BeautifulSoup(page.text,'html.parser')
    try:
        table_tag = soup.find('table')
        row_tags = table_tag.find_all('tr')
    except:
        return npulled
    obtained = [False]*len(pull_instr_ids)
    for tr_tag in row_tags:
        td_tags = tr_tag.find_all('td')
        row_name = td_tags[1].text.lower()
        for i in range(len(pull_instr_ids)):
            if pull_symbols[i] in row_name and not obtained[i]:
                obtained[i] = True
                q = float(td_tags[-1].text.replace(',', '')) * 1e9
                successfuls.append(True)
                instrument_ids.append(pull_instr_ids[i])
                quotes.append(q)
                pe_ratios.append(None)
                mkt_caps.append(None)
                div_yields.append(None)
                npulled += 1
                break
    return npulled

def get_fed_funds_quote(pull_instr_id, pull_symbol):
    npulled = 0
    root_page_addr = 'https://www.bankrate.com/rates/interest-rates/federal-funds-rate.aspx'
    page_addr = root_page_addr 
    try:
        page = requests.get(page_addr)
    except:
        return npulled
    soup = BeautifulSoup(page.text,'html.parser')
    try:
        tags = soup.find_all('td')
    except:
        return npulled
    q = None
    for i in range(len(tags)):
        if 'fed funds rate' in tags[i].text.lower():
            q = float(tags[i+1].text.strip()) / 100.
            break
    if q is None:
        return npulled
    successfuls.append(True)
    instrument_ids.append(pull_instr_id)
    quotes.append(q)
    pe_ratios.append(None)
    mkt_caps.append(None)
    div_yields.append(q)
    npulled += 1
    return npulled

def get_quote_only(pull_instr_id, pull_symbol):
    q = get_yahoo_quote(pull_symbol)
    if q is None:
        return 0
    successfuls.append(True)
    instrument_ids.append(pull_instr_id)
    quotes.append(q)
    pe_ratios.append(None)
    mkt_caps.append(None)
    div_yields.append(None)
    return 1
  
if __name__ == "__main__":
    index_id = 9 #the stock quote index
    index_id_to_host = {2:'marketwatch', -2:'marketwatch', 4:'treasury', 5:'bls.gov', 6:'yahoo', 7:'yahoo', 8:'bankrate', 9:'bea.gov'}
    
    if __debug__:
        fin = Schema(sch_name='fin', user_name='bk', host_name='kraken')
        #index_id = -2 #the stock quote index
    else:
        fin = Schema(sch_name='fin', user_name='bk')
    npull = requests_remaining(fin, 'marketwatch')
    if len(sys.argv) > 1:
        args = [a.split('=') for a in sys.argv[1:]]
        args = {a[0]:a[1] for a in args}
        if 'index_id' in args:
            index_id = int(args['index_id'])
        if 'max_pull' in args:
            npull = min(npull, int(args['max_pull']))
    host_id, day_lim, hour_lim, minute_lim = get_host_info(fin, index_id_to_host[index_id])
    fin['v_pulls_due'].select(conditions='index_id='+str(index_id))
    npull = min(len(fin['v_pulls_due']['instrument_id'].values), npull)
    pull_instr_ids = fin['v_pulls_due']['instrument_id'].values[:npull]
    fin['v_symbols'].select(conditions='host_id='+str(host_id))
    instr_id_symbols = dict(zip(fin['v_symbols']['instrument_id'].values, fin['v_symbols']['symbol'].values))
    pull_symbols = [instr_id_symbols[i] for i in pull_instr_ids]
    
    recording_time = datetime.now()
    ntotal = len(pull_instr_ids)
    npulled = 0
    if abs(index_id) == 2:
        npulled = get_stock_quotes(ntotal, pull_symbols)
    elif index_id == 4:
        npulled = get_treasury_quote(pull_instr_ids, pull_symbols)
    elif index_id == 5:
        npulled = get_cpi_quote(pull_instr_ids, pull_symbols)
    elif index_id == 6: #case-shiller
        npulled = get_quote_only(pull_instr_ids[0], pull_symbols[0])
    elif index_id == 7: #gold
        npulled = get_quote_only(pull_instr_ids[0], pull_symbols[0])
        if npulled == 1:
            quotes[-1] *= 10.
    elif index_id == 8: #fed funds rate
        npulled = get_fed_funds_quote(pull_instr_ids[0], pull_symbols[0])
    elif index_id == 9: #gdp numbers
        npulled = get_gdp_quote(pull_instr_ids, pull_symbols)
    times = [recording_time] * len(instrument_ids)
    cols = ['instrument_id', 'time_of', 'quote', 'pe_ratio', 'market_cap', 'yield']
    insert_vals = list(zip(instrument_ids, times, quotes, pe_ratios, mkt_caps, div_yields))
    fin['quotes'].insert(cols, insert_vals)
    times = [recording_time] * len(pull_instr_ids)
    index_ids = [index_id] * len(pull_instr_ids)
    cols = ['index_id', 'instrument_id', 'time_of', 'successful']
    insert_vals = list(zip(index_ids, pull_instr_ids, times, successfuls))
    fin['data_pulls'].insert(cols, insert_vals)
    print('job complete. Pulled ' + str(npulled) + ' out of ' + str(ntotal))
    