from datetime import datetime
from fin.utility import * 

class Match:
    def __init__(self):
        self.db_id = None
        self.sim_id = None
        self.sim_symbol = None
        self.sim_name = None
        self.sim_quote = None
        self.sim_mktcap = None

        self.alpha_symbol = None
        self.alpha_name = None
        self.alpha_name_match_score = None
        self.alpha_quote = None

        self.mw_symbol = None
        self.mw_name = None
        self.mw_name_match_score = None
        self.mw_quote = None
        self.mw_mktcap = None

        self.is_added = False
    
    def cols(self):
        return ['sim_id', 'symbol_alpha', 'symbol_sim', 'symbol_mw', 
        'name_alpha', 'name_sim', 'name_mw',
        'name_match_score_alpha', 'name_match_score_mw',
        'quote_alpha', 'quote_sim', 'quote_mw',
        'marketcap_sim', 'marketcap_mw', 'is_added']
   
    def to_tuple(self):
        return (self.sim_id, self.alpha_symbol, self.sim_symbol, self.mw_symbol,
        self.alpha_name, self.sim_name, self.mw_name,
        self.alpha_name_match_score, self.mw_name_match_score,
        self.alpha_quote, self.sim_quote, self.mw_quote,
        self.sim_mktcap, self.mw_mktcap, self.is_added)

def add_stock(fin, row):
    #grab statement list and look to see if it's current
    #if it isn't current, see if the symbol is already in the db
    #if it isn't in the db, reject the stock. If it is in the db,
    #use that instrument_id and add list of statements to statement_pulls
    #if it is current,
    #add instrument id
    #add to symbols for hosts 2,3,4
    #add statment list to statement_pulls
    fin['v_symbols'].select(conditions='host_id=4')
    mw_symbol_to_instrument_id = dict(zip(fin['v_symbols']['symbol'].values, fin['v_symbols']['instrument_id'].values))
    simfin_root = 'https://simfin.com/api/v1'
    statement_list = '/companies/id/' + str(row.sim_id) + '/statements/list?api-key=' + 'uQmMhU3npviy0DEptnscYIGljcbSjECF'
    page_addr = simfin_root + statement_list
    try:
        update_requests(fin, 'simfin')
        contents = requests.get(page_addr)
    except:
        return
    if contents is None:
        return
    contents = contents.json()
    def select_from_statements(statement_inputs):
        outputs = []
        for s in statement_inputs:
            if s['period'] == 'Q1':
                outputs.append( (int(s['fyear']), 1) )
            elif s['period'] == 'Q2':
                outputs.append( (int(s['fyear']), 2) )
            elif s['period'] == 'Q3':
                outputs.append( (int(s['fyear']), 3) )
            elif s['period'] == 'Q4':
                outputs.append( (int(s['fyear']), 4) )
            elif s['period'] == 'FY':
                outputs.append( (int(s['fyear']), 5) )
        return outputs
    balance_sheets = select_from_statements(contents['bs'])
    income_statements = select_from_statements(contents['pl'])
    cashflow_statements = select_from_statements(contents['cf'])
    max_year = (0,0)
    if not len(balance_sheets) == 0:
        max_year = max(balance_sheets)
    if not len(income_statements) == 0:
        max_year = max(max_year, max(income_statements))
    if not len(cashflow_statements) == 0:
        max_year = max(max_year, max(cashflow_statements))
    if max_year == (0,0) and row.db_id is None:
        row.is_added = False
        fin['match_stocks'].insert(row.cols(), [row.to_tuple()])
        return
    is_current = datetime.now().year - max_year[0] < 2
    if not is_current:
        if not row.mw_symbol in mw_symbol_to_instrument_id:
            return
        else:
            instrument_id = mw_symbol_to_instrument_id[row.mw_symbol]
    else:
        #add instrument id
        #add symbols for hosts 2,3,4
        instrument_id = fin['instruments'].last_id() + 1
        fin['instruments'].insert(['id', 'type_id'], [(instrument_id, 1)])
        fin['symbols'].insert(['instrument_id', 'host_id', 'symbol', 'name'], [(instrument_id, 2, row.alpha_symbol, row.alpha_name)])
        fin['symbols'].insert(['instrument_id', 'host_id', 'symbol', 'name'], [(instrument_id, 3, str(row.sim_id), row.sim_name)])
        fin['symbols'].insert(['instrument_id', 'host_id', 'symbol', 'name'], [(instrument_id, 4, row.mw_symbol, row.mw_name)])
    #add to statement_pulls
    cols = ['sim_id', 'instrument_id', 'statement_type_id', 'year', 'period_id']
    for s in balance_sheets:
        fin['statement_pulls'].insert(cols, [(row.sim_id, instrument_id, 1, s[0], s[1])])
    for s in income_statements:
        fin['statement_pulls'].insert(cols, [(row.sim_id, instrument_id, 2, s[0], s[1])])
    for s in cashflow_statements:
        fin['statement_pulls'].insert(cols, [(row.sim_id, instrument_id, 3, s[0], s[1])])
    row.is_added = True
    if row.db_id is None:
        fin['match_stocks'].insert(row.cols(), [row.to_tuple()])
    else:
        fin['match_stocks'].update(['id', 'is_added'], [(row.db_id, row.is_added)])

def update_statement_pulls(fin, instrument_id, sim_id=None):
    if sim_id is None:
        fin['v_symbols'].select(conditions='instrument_id='+str(instrument_id)+' and host_id=3')
        sim_id = fin['v_symbols']['symbol'][0]
    sim_id = int(sim_id)
    fin['statement_pulls'].select(conditions='sim_id=' + str(sim_id))
    db_balance_sheets = set()
    db_income_statements = set()
    db_cashflow_statements = set()
    for i in range(len(fin['statement_pulls']['id'].values)):
        if fin['statement_pulls']['statement_type_id'][i] == 1:
            db_balance_sheets.add( (fin['statement_pulls']['year'][i], fin['statement_pulls']['period_id'][i]) )
        elif fin['statement_pulls']['statement_type_id'][i] == 2:
            db_income_statements.add( (fin['statement_pulls']['year'][i], fin['statement_pulls']['period_id'][i]) )
        elif fin['statement_pulls']['statement_type_id'][i] == 3:
            db_cashflow_statements.add( (fin['statement_pulls']['year'][i], fin['statement_pulls']['period_id'][i]) )
    simfin_root = 'https://simfin.com/api/v1'
    statement_list = '/companies/id/' + str(sim_id) + '/statements/list?api-key=' + 'uQmMhU3npviy0DEptnscYIGljcbSjECF'
    page_addr = simfin_root + statement_list
    try:
        update_requests(fin, 'simfin')
        contents = requests.get(page_addr)
        if contents is None:
            return
        contents = contents.json()
    except:
        return
    def select_from_statements(statement_inputs):
        outputs = []
        for s in statement_inputs:
            if s['period'] == 'Q1':
                outputs.append( (int(s['fyear']), 1) )
            elif s['period'] == 'Q2':
                outputs.append( (int(s['fyear']), 2) )
            elif s['period'] == 'Q3':
                outputs.append( (int(s['fyear']), 3) )
            elif s['period'] == 'Q4':
                outputs.append( (int(s['fyear']), 4) )
            elif s['period'] == 'FY':
                outputs.append( (int(s['fyear']), 5) )
        return outputs
    balance_sheets = select_from_statements(contents['bs'])
    income_statements = select_from_statements(contents['pl'])
    cashflow_statements = select_from_statements(contents['cf'])
    cols = ['sim_id', 'instrument_id', 'statement_type_id', 'year', 'period_id']
    for s in balance_sheets:
        if not s in db_balance_sheets:
            fin['statement_pulls'].insert(cols, [(sim_id, instrument_id, 1, s[0], s[1])])
    for s in income_statements:
        if not s in db_income_statements:
            fin['statement_pulls'].insert(cols, [(sim_id, instrument_id, 2, s[0], s[1])])
    for s in cashflow_statements:
        if not s in db_cashflow_statements:
            fin['statement_pulls'].insert(cols, [(sim_id, instrument_id, 3, s[0], s[1])])