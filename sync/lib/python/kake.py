'''
Created on Feb 7, 2018

@author: bk
'''
import os
import subprocess
import sys

def usage():
    print('kake [-f file] [file-arg]')

if __name__ == '__main__':
    arg = []
    if (len(sys.argv) < 3):
        kfileSearch = ['kakefile.py','Kakefile.py','kakefile','Kakefile']
        kfile = ''
        for f in kfileSearch:
            if (os.path.exists(f)):
                kfile = f
                break
        if (kfile == ''):
            usage()
            sys.exit(1)
        if (len(sys.argv) == 2):
            arg = [sys.argv[1]]
    elif (not sys.argv[2] == '-f'):
        usage()
        sys.exit(1)
    else:
        kfile = sys.argv[2]
        if (len(sys.argv) >= 4):
            arg = sys.argv[3:]
    args = ['python',kfile]
    args.extend(arg)
    subprocess.call(args)
    sys.exit(0)