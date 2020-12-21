from findb import Symbol
from indicator import AoA
import os

if __name__ == '__main__':
    tickName=['ethereum', 'fluz-fluz']
    for tn in tickName:
        sym = Symbol(tn)
        sym.read()
        numVal = len(sym.date)
        #use the last 365 days only
        sym.date = sym.date[-min(numVal,365):]
        sym.open = sym.open[-min(numVal,365):]
        sym.high = sym.high[-min(numVal,365):]
        sym.low = sym.low[-min(numVal,365):]
        sym.close = sym.close[-min(numVal,365):]
        sym.mktcap = sym.mktcap[-min(numVal,365):]
        sym.volume = sym.volume[-min(numVal,365):]
        aoa=AoA(sym)
        aoa.generateSignal()
        aoa.write()
    cwd=os.getcwd()
    os.chdir(Symbol.dataDir)
    os.system('git add -A :/')
    os.system('git commit -m automated')
    os.system('git push')
    os.chdir(cwd)