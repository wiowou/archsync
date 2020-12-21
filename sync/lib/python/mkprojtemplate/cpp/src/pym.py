from make import Source,Target,Makefile
from make.compiler.gpp import Exe, Shared

import glob
import os

if __name__ == '__main__':
    targetName='coll'
    debug=True
    binType='lib'
    
    binOutputDir='../bin'
    if debug:
        binOutputDir='../debug'
    if binType == 'exe':
        bname=os.path.join(binOutputDir,targetName)
        binary=Exe()
    elif binType == 'lib':
        bname=os.path.join(binOutputDir,'lib'+targetName+'.so')
        binary=Shared()
    if debug:
        binary.options+='-g -G -DMYDEBUG'

    #binary.includeDir = ['mysubDir']
    
    binTarg=Target(bname,binary)
    binTarg.source=[]
    
    cFiles=glob.glob1('.','*.cpp') #list all .cpp files in the current directory
    for f in cFiles:
        binTarg.source.append(Source(f))
    
    binTarg.target=[]
    cFiles=glob.glob1('cuda','*.h') #list all .h files in the current directory
    for f in cFiles:
        binTarg.target.append(Source(f))

    makefile=Makefile()
    makefile.target=[binTarg]
    makefile.write()
