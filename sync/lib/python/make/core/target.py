import os 

from make.compiler import Compiler

class Target(object):
    def __init__(self,name,compiler=Compiler()):
        self.name = name
        self.compiler = compiler
        self.target = []
        self.source = []
    
    def callName(self):
        return os.path.basename(self.name)
    
    def __str__(self):
        s = ''
        callName = self.callName()
        if (not self.name == callName):
            s += callName + ' : ' + self.name + '\n'
            #s += '\t echo \n' 
        s += self.name + ' : '
        for t in self.target:
            s += t.name + ' '
        objStr = ''
        objName = []
        for r in self.source:
            objStr += r.objName() + ' '
            objName.append(r.objName())
        s += objStr + '\n'
        s += '\t' + self.compiler._buildCommand_(objName, self.name) + '\n'
        return s