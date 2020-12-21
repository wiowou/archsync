'''
Created on Feb 6, 2018

@author: bk
'''
from make.compiler import Compiler

class MS_Compiler(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.includeDir = []
        self.options = []

    def _sourceToObjectCommand_(self,objFileName,srcName):
        opt = ' '
        for o in self.options:
            opt += ' /' + o
        idir = ''
        for i in self.includeDir:
            idir += ' /I' + i
        return self.cmdName + ' /c' + idir + opt + ' /Fo' + objFileName + ' ' + srcName
    
    def _findIncludeFiles_(self, srcName):
        idep = []
        with open(srcName,'r') as f:
            for line in f:
                line = line.strip()
                if ('#include ' in line):
                    words = line.split()
                    i = words[1].strip()
                    i = i[1:-1]
                    idep.append(i)
        return idep

class MS_Exe(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        #self.includeDir = []
        self.library = [] #examples are add.lib
        self.options = []

    def _buildCommand_(self,objNames,targetName):
        opt = ' '
        for o in self.options:
            opt += ' /' + o
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        idir = ''
        for i in self.includeDir:
            idir += ' /I' + i
        lib = ' '
        for l in self.library:
            lib += ' ' + l
        return self.cmdName + opt + objects + ' /Fe' + targetName + idir + lib

class SharedLib(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.includeDir = []
        self.libraryDir = []
        self.library = []
        self.options = []

    def _buildCommand_(self,objNames,targetName):
        opt = ' -shared -fPIC '
        for o in self.options:
            opt += ' -' + o
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        ldir = ''
        for l in self.libraryDir:
            ldir += ' -L' + l
        idir = ''
        for i in self.includeDir:
            idir += ' -I' + i
        lib = ''
        if (len(self.library) > 0):
            lib = '-Wl,--whole-archive'
        for l in self.library:
            lib += ' -l' + l
        if (len(self.library) > 0):
            lib += ' -Wl,--no-whole-archive'
        return self.cmdName + opt + objects + ' -o ' + targetName + ldir + idir + lib

class StaticLib(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.name = 'MS_archiver'
        self.options = ['/EHsc']

    def _buildCommand_(self,objNames,targetName):
        opt = ' '
        for o in self.options:
            opt += o
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        return 'lib' + opt + ' /Fo' + targetName + objects
        
class CC(MS_Compiler):
    def __init__(self):
        MS_Compiler.__init__(self)
        self.cmdName = 'cl'
        self.name = 'MS_c++'
        self.ext = ['cpp','cxx','CC','CXX','cc','c++','C']
        self.exclude = []

class Exe(MS_Exe,CC):
    def __init__(self):
        Exe.__init__(self)
        CC.__init__(self)
        self.name = 'MS_c++_exe'

class Shared(SharedLib,CC):
    def __init__(self):
        SharedLib.__init__(self)
        CC.__init__(self)
        self.options = ['fPIC']
        self.name = 'gnu_c++_shared'

class Static(StaticLib,CC):
    def __init__(self):
        StaticLib.__init__(self)
        CC.__init__(self)
        self.name = 'MS_c++_static'

