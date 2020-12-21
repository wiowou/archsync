#!/usr/bin/python
import sys
from dbcon.postgres import Schema
from fin.utility import * 
from fin.match_utility import * 

#updates the list of statements that need to be pulled for each of the active instruments
#scheduled for the 1st of every month

if __name__ == "__main__":
    if __debug__:
        fin = Schema(sch_name='fin', user_name='bk', host_name='kraken')
    else:
        fin = Schema(sch_name='fin', user_name='bk')
    npull = requests_remaining(fin, 3)
    if len(sys.argv) > 1:
        args = [a.split('=') for a in sys.argv[1:]]
        args = {a[0]:a[1] for a in args}
        if 'max_pull' in args:
            npull = min(npull, int(args['max_pull']))

    fin['v_symbols'].select(conditions='host_id=3 order by instrument_id')
    instr_id_sim_id = dict(zip(fin['v_symbols']['instrument_id'].values, fin['v_symbols']['symbol'].values))
    tb = fin['v_symbols']
    npull = min(npull, len(tb['id'].values))
    for i in range(npull):
        update_statement_pulls(fin, tb['instrument_id'][i], tb['symbol'][i])
    print('job complete.')
