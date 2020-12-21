import os

class Compiler(object):
    def __init__(self):
        self.name = ''
        self.cmdName = ''
        self.options = ''
        self.includeDir = []
        self.ext = []
        self.exclude = []
    
    def vcmd(self):
        return '${CC' + self.name + '}'
    
    def voptions(self):
        return '${OP' + self.name + '}'
    
    def headerDep(self,srcName):
        allHdr = self._findIncludeFiles_(srcName)
        #only keep the headers that exist in the root directory
        hdr = []
        for i in allHdr:
            #i = os.path.realpath(i)
            if (os.path.exists(i)):
                hdr.append(i)
            else:
                for d in self.includeDir:
                    #d = os.path.realpath(d)
                    di = os.path.join(d,i)
                    if (os.path.exists(di)):
                        hdr.append(di)
                        break
        return hdr
    
    def _findIncludeFiles_(self, srcName):
        idep = []
        return idep
    
    def _sourceToObjectCommand_(self,objFileName,srcName):
        return 'echo '
    
    def _buildCommand_(self,objNames,targetName):
        return 'echo '
        
    def __str__(self):
        s = self.vcmd()[2:-1] + ' = ' + self.cmdName + '\n'
        s += self.voptions()[2:-1] + ' = ' + self.options + '\n'
        return s