from make.compiler import Compiler

class GNU_Compiler(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.options = ''
    
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

class GNUExe(Compiler):
    def __init__(self):
        Compiler.__init__(self)
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
        ldir = ''
        for l in self.libraryDir:
            ldir += ' -L' + l
        libso = ''
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
        lib = liba + libso
        if (len(lib) > 0):
            lib += ' '
        s = self.vcmd() + ' ' + self.voptions() + self._incStr_()  + ldir + lib + objects
        s += ' -o ' + targetName
        return s

class SharedLib(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.includeDir = []
        self.libraryDir = []
        self.library = []
        self.options = '-fPIC '

    def _buildCommand_(self,objNames,targetName):
        opt = '-shared ' + self.voptions()
        objects = ''
        for o in objNames:
            objects += ' ' + o
        ldir = ' '
        for l in self.libraryDir:
            ldir += ' -L' + l
        lib = ' '
        if (len(self.library) > 0):
            lib = '-Wl,--whole-archive'
        for l in self.library:
            lib += ' -l' + l
        if (len(self.library) > 0):
            lib += ' -Wl,--no-whole-archive'
        if (len(lib) > 0):
            lib += ' '
        return self.vcmd() + opt + self._incStr_() + ldir + lib + objects + ' -o ' + targetName

class StaticLib(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.name = 'gnu_archiver'
        self.options = 'rcs'

    def _buildCommand_(self,objNames,targetName):
        opt = ' ' + self.options
        objects = ' '
        for o in objNames:
            objects += ' ' + o
        return 'ar' + opt + ' ' + targetName + objects
        
class CC(GNU_Compiler):
    def __init__(self):
        GNU_Compiler.__init__(self)
        self.cmdName = 'g++'
        self.name = 'gp'
        self.ext = ['cpp','cxx','CC','CXX','cc','c++','C']
        self.exclude = []

class Exe(GNUExe,CC):
    def __init__(self):
        GNUExe.__init__(self)
        CC.__init__(self)
        self.name = 'gpe'

class Shared(SharedLib,CC):
    def __init__(self):
        SharedLib.__init__(self)
        CC.__init__(self)
        self.options = 'fPIC'
        self.name = 'gps'

class Static(StaticLib,CC):
    def __init__(self):
        StaticLib.__init__(self)
        CC.__init__(self)
        self.name = 'gpa' 