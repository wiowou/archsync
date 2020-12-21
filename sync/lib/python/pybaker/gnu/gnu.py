'''
Created on Jan 2, 2018

@author: bk
'''
from pybaker.core import Compiler

class GNU_Compiler(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.compilerOptions = []

    def _sourceToObjectCommand_(self,objFileName,srcName):
        opt = ' '
        for o in self.compilerOptions:
            opt += ' -' + o
        idir = ''
        for i in self.includeDir:
            idir += ' -I' + i
        return self.cmdName + ' -c' + idir + opt + ' -o ' + objFileName + ' ' + srcName
    
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

class Exe(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.includeDir = []
        self.libraryDir = []
        self.library = [] #examples are libadd.so, libadd.a
        self.exeOptions = []

    def _buildCommand_(self,objNames,targetName):
        sharedLibrary = [e for e in self.library if e[-3:] == '.so']
        staticLibrary = [e for e in self.library if e[-2:] == '.a']
        opt = ' '
        for o in self.exeOptions:
            opt += '-' + o + ' '
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        ldir = ''
        for l in self.libraryDir:
            ldir += ' -L' + l
        idir = ''
        for i in self.includeDir:
            idir += ' -I' + i
        libso = ' '
        if len(sharedLibrary) > 0 and len(staticLibrary) > 0:
            libso = ' -Wl,-Bdynamic'
        for l in sharedLibrary:
            libso += ' -l' + l[3:-3]
        liba = ''
        if len(staticLibrary) > 0:
            liba = ' -Wl,-Bstatic'
            if (len(sharedLibrary) == 0):
                liba = ' -static'
        for l in staticLibrary:
            liba += ' -l' + l[3:-2]
        return self.cmdName + opt + objects + ' -o ' + targetName + ldir + idir + liba + libso

class SharedLib(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.includeDir = []
        self.libraryDir = []
        self.library = []
        self.libOptions = []

    def _buildCommand_(self,objNames,targetName):
        opt = ' -shared -fPIC '
        for o in self.libOptions:
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
        self.name = 'gnu_archiver'
        self.libOptions = ['r','c','s']

    def _buildCommand_(self,objNames,targetName):
        opt = ' '
        for o in self.libOptions:
            opt += o
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        return 'ar' + opt + ' ' + targetName + objects
        
class CPP(GNU_Compiler):
    cmdName = 'g++'
    def __init__(self):
        GNU_Compiler.__init__(self)
        self.name = 'gnu_c++'
        self.ext = ['cpp','cxx','CPP','CXX','cc','c++','C']
        self.exclude = []

class CPP_Exe(Exe,CPP):
    def __init__(self):
        Exe.__init__(self)
        CPP.__init__(self)
        self.name = 'gnu_c++_exe'

class CPP_Shared(SharedLib,CPP):
    def __init__(self):
        SharedLib.__init__(self)
        CPP.__init__(self)
        self.compilerOptions = ['fPIC']
        self.name = 'gnu_c++_shared'

class CPP_Static(StaticLib,CPP):
    def __init__(self):
        StaticLib.__init__(self)
        CPP.__init__(self)
        self.name = 'gnu_c++_static' 