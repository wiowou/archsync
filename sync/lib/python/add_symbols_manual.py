#!/usr/bin/python
from dbcon.postgres import Schema
from fin.utility import * 
from fin.match_utility import * 

def create_symbols(fin):
    fin['v_good_matches'].select(conditions='is_added=False')
    ids = fin['v_good_matches']['id'].values
    sim_ids = fin['v_good_matches']['sim_id'].values
    sim_symbols = fin['v_good_matches']['symbol_sim'].values
    sim_names = fin['v_good_matches']['name_sim'].values
    sim_quotes = fin['v_good_matches']['quote_sim'].values
    sim_mktcaps = fin['v_good_matches']['marketcap_sim'].values
    alpha_symbols = fin['v_good_matches']['symbol_alpha'].values
    alpha_names = fin['v_good_matches']['name_alpha'].values
    alpha_name_match_scores = fin['v_good_matches']['name_match_score_alpha'].values
    alpha_quotes = fin['v_good_matches']['quote_alpha'].values
    mw_symbols = fin['v_good_matches']['symbol_mw'].values
    mw_names = fin['v_good_matches']['name_mw'].values
    mw_name_match_scores = fin['v_good_matches']['name_match_score_mw'].values
    mw_quotes = fin['v_good_matches']['quote_mw'].values
    mw_mktcaps = fin['v_good_matches']['marketcap_mw'].values
    for i in range(len(ids)):
        row = Match()
        row.db_id = ids[i]
        row.sim_id = sim_ids[i]
        row.sim_symbol = sim_symbols[i]
        row.sim_name = sim_names[i]
        row.sim_quote = sim_quotes[i]
        row.sim_mktcap = sim_mktcaps[i]
        row.alpha_symbol = alpha_symbols[i]
        row.alpha_name = alpha_names[i]
        row.alpha_name_match_score = alpha_name_match_scores[i]
        row.alpha_quote = alpha_quotes[i]
        row.mw_symbol = mw_symbols[i]
        row.mw_name = mw_names[i]
        row.mw_name_match_score = mw_name_match_scores[i]
        row.mw_quote = mw_quotes[i]
        row.mw_mktcap = mw_mktcaps[i]
        add_stock(fin, row)

if __name__ == "__main__":
    if __debug__:
        fin = Schema(sch_name='fin', user_name='bk', host_name='kraken')
    else:
        fin = Schema(sch_name='fin', user_name='bk')
    create_symbols(fin)