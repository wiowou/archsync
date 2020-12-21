'''
Created on Feb 3, 2018

@author: bk
'''
from make.compiler import Compiler

class CC(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.cmdName = 'nvcc'
        self.name = 'nv'
        self.options = ''
        self.ext = ['cu','CU','cpp','cxx','CPP','CXX','cc','c++','C','c']
    
    def _incStr_(self):
        idir = ''
        j = 0
        for i in self.includeDir:
            if (j == 0):
                idir += ' -I' + i
            else:
                idir += ',' + i
            j += 1
        return idir + ' '    
    
    def _sourceToObjectCommand_(self,objFileName,srcName):
        s = self.vcmd() + ' ' + self.voptions() + self._incStr_() + srcName
        s += ' -o ' + objFileName
        return s
    
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

class Exe(CC):
    def __init__(self):
        CC.__init__(self)
        self.name = 'nve'
        self.includeDir = []
        self.libraryDir = []
        self.library = [] #examples are libadd.so, libadd.a
        self.options = ''

    def _buildCommand_(self,objNames,targetName):
        sharedLibrary = [e for e in self.library if e[-3:] == '.so']
        staticLibrary = [e for e in self.library if e[-2:] == '.a']
        objects = ''
        for o in objNames:
            objects += ' ' + o
        ldir = ' '
        for l in self.libraryDir:
            ldir += ' -L' + l
        libso = ' '
        if len(sharedLibrary) > 0 and len(staticLibrary) > 0:
            libso = " --compiler-options '-Wl,-Bdynamic'"
        for l in sharedLibrary:
            libso += ' -l' + l[3:-3]
        liba = ' '
        if len(staticLibrary) > 0:
            liba = " --compiler-options '-Wl,-Bstatic'"
            if (len(sharedLibrary) == 0):
                liba = ' -static'
        for l in staticLibrary:
            liba += ' -l' + l[3:-2]
        lib = liba + libso
        if (len(lib) > 0):
            lib += ' '
        s = self.vcmd() + ' ' + self.voptions() + self._incStr_()  + ldir + lib + objects
        s += ' -o ' + targetName 
        return s

class Shared(CC):
    def __init__(self):
        CC.__init__(self)
        self.name = 'nvs'
        self.options = "--compiler-options '-fPIC' "
        self.includeDir = []
        self.libraryDir = []
        self.library = []

    def _buildCommand_(self,objNames,targetName):
        opt = ' --shared ' + self.voptions()
        objects = ''
        for o in objNames:
            objects += o + ' '
        ldir = ''
        for l in self.libraryDir:
            ldir += ' -L' + l
        lib = ''
        #if (len(self.library) > 0):
        #    lib = "--compiler-options '-Wl,--whole-archive'"
        for l in self.library: #assume that only static libs are linked to dynamic libs
            lib += ' -l' + l[3:-3]
        #if (len(self.library) > 0):
        #    lib += "--compiler-options '-Wl,--no-whole-archive'"
        if (len(lib) > 0):
            lib += ' '
        return self.vcmd() + opt + self._incStr_() + ldir + lib + objects + '-o ' + targetName

class Static(CC):
    def __init__(self):
        CC.__init__(self)
        self.name = 'nva'
        self.options = '--lib'

    def _buildCommand_(self,objNames,targetName):
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        return self.vcmd() + ' ' + self.voptions() + ' ' + targetName + objects

class HostLinkObject(CC):
    def __init__(self):
        CC.__init__(self)
        self.name = 'nvh'

    def _buildCommand_(self,objNames,targetName):
        opt = ' --device-link ' + self.voptions()
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        return self.vcmd() + opt + ' -o ' + targetName + objects
