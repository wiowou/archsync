import os
import subprocess
import sys

def usage():
    print('pym [function-name]')

if __name__ == '__main__':
    fileSearch = ['pym.py','pym']
    pf = ''
    for f in fileSearch:
        if (os.path.exists(f)):
            pf = f
            break
    narg = len(sys.argv)
    if (pf == '' or narg > 2):
        usage()
        sys.exit(1)
    subprocess.call(['python',pf])
    if (narg > 1):
        pf = pf.split('.py')[0]
        cmd = "python -c 'import "+pf+';'+pf+'.'+sys.argv[1]+"()'"    
    sys.exit(0)