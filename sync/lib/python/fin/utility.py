from dbcon.postgres import Schema
from datetime import datetime
import time
from bs4 import BeautifulSoup
import requests 

def simplify_instrument_name(s):
    if s is None:
        return None
    s = s.split('/')[0].strip()
    s = s.split('\\')[0].strip()
    s = s.lower()
    if s[-4:] == 'cl a':
        s = s[:-4]
    if s[-4:] == 'cl b':
        s = s[:-4]
    if s[-4:] == 'cl c':
        s = s[:-4]
    if s[-4:] == 'cl 1':
        s = s[:-4]
    if s[-4:] == 'cl 2':
        s = s[:-4]
    if s[-4:] == ' adr':
        s = s[:-4]
    if s[-4:] == ' cos':
        s = s[:-4]
    s = s.replace(' class a','')
    s = s.replace(' class b','')
    s = s.replace(' class c','')
    s = s.replace(',','')
    s = s.replace('.com','')
    s = s.replace('.','')
    s = s.replace('-',' ')
    s = s.replace('*','')
    s = s.replace('(','')
    s = s.replace(')','')
    s = s.replace(' & ',' ')
    s = s.replace(' a ',' ')
    s = s.replace(' corporation','') 
    s = s.replace(' incorporated','') 
    s = s.replace(' corp','') 
    s = s.replace(' company','') 
    s = s.replace(' companies','') 
    s = s.replace(" int'l",'') 
    s = s.replace(' international','') 
    s = s.replace(' limited','') 
    s = s.replace(' ltd','') 
    s = s.replace(' llc','') 
    s = s.replace(' plc','') 
    s = s.replace(' group','') 
    s = s.replace(' bancorporation','bancorp') 
    s = s.replace(' health care','healthcare') 
    s = s.replace("'",'') 
    s = s.strip()
    if s[-3:] == ' sa':
        s = s[:-3]
    if s[-3:] == ' de':
        s = s[:-3]
    if s[-3:] == ' nv':
        s = s[:-3]
    if s[-4:] == ' n v':
        s = s[:-4]
    if s[:4] == 'the ':
        s = s[4:]
    if s[-3:] == ' co':
        s = s[:-3]
    if s[-4:] == ' inc' or s[-4:] == ' cos':
        s = s[:-4]
    if s[-3:] == ' co':
        s = s[:-3]
    if s[-3:] == ' lp':
        s = s[:-3]
    if s[-4:] == ' l p':
        s = s[:-4]
    return s

def get_host_info(db, hostname):
    db['hosts'].select()
    for i in range(len(db['hosts']['name'].values)):
        if hostname in db['hosts']['name'][i]:
            return db['hosts']['id'][i], db['hosts']['day_limit'][i], db['hosts']['hour_limit'][i], db['hosts']['minute_limit'][i]
    return None

def update_requests(db, host, number_of_requests=1):
    cols = ['host_id', 'number_of']
    id = host
    if not isinstance(host, int):
        id, _, _, _ = get_host_info(db, host)
    insert_vals = [(id, number_of_requests)]
    db['requests'].insert(cols, insert_vals)

def requests_remaining(db, host):
    if isinstance(host, int):
        db['v_last_requests'].select(conditions="host_id=" + str(host))
    else:
        db['v_last_requests'].select(conditions="hostname like '%" + host + "%'")
    if len(db['v_last_requests']['host_id'].values) == 0:
        return float('inf')
    req_limit = float('inf')
    if not db['v_last_requests']['request_limit'][0] is None:
        req_limit = db['v_last_requests']['request_limit'][0]
    res = req_limit 
    if not db['v_last_requests']['day'][0] is None and db['v_last_requests']['day'][0].date() == datetime.now().date():
        tot_req = 0
        if not db['v_last_requests']['total_requests'][0] is None:
            tot_req = db['v_last_requests']['total_requests'][0]
        res = req_limit - tot_req
    return res

def name_match_score(name, name_ck):
    ns = set(name.split())
    ns_ck = set(name_ck.split())
    nspaces = name.count(' ') + name_ck.count(' ')

    in_ns_ck = ns_ck - ns
    in_both = ns_ck - in_ns_ck
    num_in_both = 0
    for n in in_both:
        num_in_both += 2*len(n)
    return num_in_both / (len(name) + len(name_ck) - nspaces)

def get_alphavantage_quote(symbol, sleep_time=12.1):
    base_addr = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='
    apikey = '14QC5OD0TJP61MGS'
    page_addr = base_addr + symbol + '&apikey=' + apikey
    quote = {'open':None, 'high':None, 'low':None, 'last':None, 'volume':None, 'date':None}
    try:
        contents = requests.get(page_addr)
    except:
        return None 
    if contents is None:
        return None 
    time.sleep(sleep_time)
    data = contents.json()
    quote['last'] = float(data['Global Quote']['05. price'])
    quote['open'] = float(data['Global Quote']['02. open'])
    quote['high'] = float(data['Global Quote']['03. high'])
    quote['low'] = float(data['Global Quote']['04. low'])
    quote['volume'] = float(data['Global Quote']['06. volume'])
    quote['date'] = datetime.strptime(data['Global Quote']['07. latest trading day'], '%Y-%m-%d')
    return quote

def get_marketwatch_quote(symbol):
    root_page_addr = 'https://www.marketwatch.com/investing/stock/'
    page_addr = root_page_addr + symbol
    result = {}
    try:
        page = requests.get(page_addr)
    except:
        return None
    #html = page.read()
    #with open('inout/page.html', 'w') as f:
    #    f.write(page.text)
    soup = BeautifulSoup(page.text,'html.parser')
    try:
        result['quote'] = float(soup.find('bg-quote', {'class' : 'value', 'field' : 'Last'}).text)
        name_tag = soup.find('meta', {'name' : 'name'})
        result['name'] = simplify_instrument_name(name_tag.attrs['content'])
    except:
        try:
            price_tag = soup.find('meta', {'name' : 'price'})
            result['quote'] = float(price_tag.attrs['content'].replace(',', ''))
            name_tag = soup.find('meta', {'name' : 'name'})
            result['name'] = simplify_instrument_name(name_tag.attrs['content'])
        except:
            return None
    #tags = soup.find(name='h2', text='Key Data')
    tags = soup.find(text='Key Data')
    tags = tags.find_parent(name='div')
    tags = tags.contents[3].contents
    result['div_yield'] = None
    result['pe_ratio'] = None
    result['mkt_cap'] = None
    result['currency'] = 'USD'
    for tag in tags:
        if tag == '\n' or len(tag.contents) < 3:
            continue
        if tag.contents[1].text == 'Market Cap' and not tag.contents[3].text.lower().startswith('n'):
            mkt_cap = tag.contents[3].text
            if mkt_cap[0] == '$':
                result['currency'] = 'USD'
            elif mkt_cap[0] == chr(8364):
                result['currency'] = 'EUR'
            elif mkt_cap[0] == chr(163):
                result['currency'] = 'GBP'
            else:
                result['currency'] = 'OTHER'
            for _ in range(len(mkt_cap) - 1):
                if not mkt_cap[0].isdigit():
                    mkt_cap = mkt_cap[1:]
                else:
                    continue
            if 'T' in mkt_cap:
                mkt_cap = float(mkt_cap[:-1]) * 1e12
            elif 'B' in mkt_cap:
                mkt_cap = float(mkt_cap[:-1]) * 1e9
            elif 'M' in mkt_cap:
                mkt_cap = float(mkt_cap[:-1]) * 1e6
            elif 'K' in mkt_cap:
                mkt_cap = float(mkt_cap[:-1]) * 1e3
            result['mkt_cap'] = mkt_cap
        if tag.contents[1].text == 'P/E Ratio' and not tag.contents[3].text.lower().startswith('n'):
            pe_ratio = tag.contents[3].text
            pe_ratio = pe_ratio.replace(',', '')
            try:
                result['pe_ratio'] = float(pe_ratio)
            except:
                result['pe_ratio'] = None
        if tag.contents[1].text == 'Yield' and not tag.contents[3].text.lower().startswith('n'):
            result['div_yield'] = float(tag.contents[3].text[:-1])
    return result

def get_yahoo_quote(symbol):
    root_page_addr = 'https://finance.yahoo.com/quote/'
    page_addr = root_page_addr + symbol 
    try:
        page = requests.get(page_addr)
    except:
        return None
    soup = BeautifulSoup(page.text,'html.parser')
    try:
        tag = soup.find('div', {'id' : 'quote-header-info'})
        tag = list(tag.children)[-1].find('div').find('span')
        q = float(tag.text)
    except:
        return None
    return q

def columnize_name(s, tid):
    s = s.lower().strip()
    s = s.replace(',','')
    s = s.replace('-',' ')
    s = s.replace('/',' ')
    s = s.replace(' & ',' ')
    s = s.replace('(','')
    s = s.replace(')','')
    s = s.replace(' of ',' ')
    s = s.replace(' and ',' ')
    s = s.replace(' in ',' ')
    s = s.replace(' for ',' ')
    s = s.replace(' a ',' ')
    s = s.replace(' from ',' ')
    words = s.split()
    ret = ''
    for w in words:
        ret += w[0]
    return ret + '_' + str(tid)
 