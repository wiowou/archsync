#!/usr/bin/python
import sys
from dbcon.postgres import Schema
from fin.utility import * 

#balance, income, cashflow statements
#daily until historical statements obtained

def get_statement_data(fin, instrument_id, sim_id, statement_type_id, period_type_id, year, pull_id, statement_types, period_types):
    statement_type = statement_types[statement_type_id]
    period_type = period_types[period_type_id]
    simfin_root = 'https://simfin.com/api/v1'
    std_stat = '/companies/id/' + str(sim_id) + '/statements/standardised' + '?api-key=uQmMhU3npviy0DEptnscYIGljcbSjECF'
    std_stat += '&stype=' + str(statement_type) + '&ptype=' + str(period_type) + '&fyear=' + str(year)
    page_addr = simfin_root + std_stat
    try:
        update_requests(fin, 'simfin')
        contents = requests.get(page_addr)
        if contents is None:
            print('wget no contents sim_id: ' + str(sim_id) + ' statement_type: ' + str(statement_type) + ' period_type: ' + str(period_type) + ' year: ' + str(year))
            return 0
        stmt = contents.json()
    except:
        print('wget exception sim_id: ' + str(sim_id) + ' statement_type: ' + str(statement_type) + ' period_type: ' + str(period_type) + ' year: ' + str(year))
        return 0
    if 'error' in stmt:
        print('not found sim_id: ' + str(sim_id) + ' statement_type: ' + str(statement_type) + ' period_type: ' + str(period_type) + ' year: ' + str(year))
        fin['statement_pulls'].update(['id', 'not_found'], [(pull_id, True)])
        return 0
    if statement_type_id == 1:
        tb = fin['balance_stmts']
    elif statement_type_id == 2:
        tb = fin['income_stmts']
    elif statement_type_id == 3:
        tb = fin['cashflow_stmts']
    if stmt['industryTemplate'] == 'banks':
        if statement_type_id == 1:
            tb = fin['bank_balance_stmts']
        elif statement_type_id == 2:
            tb = fin['bank_income_stmts']
        elif statement_type_id == 3:
            tb = fin['bank_cashflow_stmts']
        pass
    elif stmt['industryTemplate'] == 'insurances':
        if statement_type_id == 1:
            tb = fin['insurance_balance_stmts']
        elif statement_type_id == 2:
            tb = fin['insurance_income_stmts']
        elif statement_type_id == 3:
            tb = fin['insurance_cashflow_stmts']
        pass
    all_null = True
    col_names = ['instrument_id', 'period_id', 'year']
    vals = [instrument_id, period_type_id, year]
    for v in stmt['values']:
        col_name = columnize_name(v['standardisedName'], int(v['tid']))
        val_chosen = v['valueChosen']
        if col_name in tb.columns and not val_chosen is None:
            col_names.append(col_name)
            vals.append(float(val_chosen))
            all_null = False
    if not all_null:
        tb.insert(col_names, [tuple(vals)])
    else:
        print('all null sim_id: ' + str(sim_id) + ' statement_type: ' + str(statement_type) + ' period_type: ' + str(period_type) + ' year: ' + str(year))
    fin['statement_pulls'].update(['id', 'obtained', 'all_null'], [(pull_id, not all_null, all_null)])
    return 1
    
if __name__ == "__main__":
    if __debug__:
        fin = Schema(sch_name='fin', user_name='bk', host_name='kraken')
    else:
        fin = Schema(sch_name='fin', user_name='bk')
    npull = requests_remaining(fin, host='simfin') 
    pull_type = 'fy'
    if len(sys.argv) > 1:
        args = [a.split('=') for a in sys.argv[1:]]
        args = {a[0]:a[1] for a in args}
        if 'max_pull' in args:
            npull = min(npull, int(args['max_pull']))
        if 'pull_type' in args:
            pull_type = args['pull_type']
    fin['period_types'].select()
    period_types = dict(zip(fin['period_types']['id'].values, fin['period_types']['abbreviation'].values))
    fin['statement_types'].select()
    statement_types = dict(zip(fin['statement_types']['id'].values, fin['statement_types']['abbreviation'].values))
    table_name = 'v_statement_pulls_due_' + pull_type
    fin[table_name].select()
    tb = fin[table_name]
    npull = min(npull, len(tb['id'].values))
    npulled = 0
    for i in range(npull):
        npulled += get_statement_data(
            fin, 
            tb['instrument_id'][i], 
            tb['sim_id'][i], 
            tb['statement_type_id'][i], 
            tb['period_id'][i], 
            tb['year'][i], 
            tb['id'][i], 
            statement_types, 
            period_types)
    print('job complete. Pulled ' + str(npulled))
