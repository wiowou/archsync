'''
Created on Nov 19, 2017

@author: 
'''
import os
from pybaker.core import piesDir
from pybaker.core import objectFileExt

class Compiler(object):
    cmdName = ''
    def __init__(self):
        self.name = ''
        self.ext = []
        self.exclude = []
        self.includeDir = []
    
    def needsCompilation(self,srcName,hdr):
        if (not os.path.exists(srcName)):
            return True
        needsToBeCompiled = False
        objFileName = self.objFileName(srcName)
        metaFileName = objFileName + '.meta'
        metaFileName = os.path.realpath(metaFileName)
        #self._makeDirectories_(metaFileName)
        lastModTime = int(os.path.getmtime(srcName))
        if (not os.path.exists(metaFileName)):
            needsToBeCompiled = True
        else: #read in last time of compilation and compare to srcName's mod time
            fin = open(metaFileName,'r')
            lastCompileTime = fin.readline().strip()
            fin.close()
            if (lastCompileTime == ''):
                lastCompileTime = 0
            lastCompileTime = int(lastCompileTime)
            if (lastModTime > lastCompileTime):
                needsToBeCompiled = True
        needsToBeCompiled = self._checkIncludeFiles_(srcName,hdr) or needsToBeCompiled
        return needsToBeCompiled
    
    def compileCmd(self,srcName):
        objFileName = self.objFileName(srcName)
        return self._sourceToObjectCommand_(objFileName,srcName)
        
    
    def _makeDirectories_(self, fileName):
        d = os.path.dirname(fileName)
        if (not os.path.exists(d)):
            os.makedirs(d)
    
    def objFileName(self,srcName):
        head,tail = os.path.split(srcName)
        if (len(head) > 1 and head[1] == '\\'):
            head = head[2:]
        elif (len(head) > 0 and (head[0] == '\\' or head[0] == '/')):
            head = head[1:]
        if (not head == ''):
            head += '-'
        head = head.replace('/','-')
        head = head.replace('\\','-')
        head = head.replace('..','up')
        head = head.replace('.','-')
        tail = self.name + '___' + head + tail + objectFileExt
        objFileName = os.path.join(piesDir,tail)
        return objFileName
        
    def isMatch(self,srcName):
        for e in self.ext:
            size = len(e)
            if (srcName[-size:] == e):
                for x in self.exclude:
                    size2 = len(x)
                    if (srcName[-size2:] == x):
                        return False
                return True
        return False
    
    def _sourceToObjectCommand_(self,objFileName,srcName):
        return 'echo ' + objFileName + ' ' + srcName

    def _buildCommand_(self,objNames,targetName):
        return 'echo buildCommand'
    
    def _findIncludeFiles_(self,srcName):
        idep = []
        return idep
    
    def headerDep(self,srcName):
        allHdr = self._findIncludeFiles_(srcName)
        #only keep the headers that exist in the root directory
        hdr = []
        for i in allHdr:
            i = os.path.realpath(i)
            if (os.path.exists(i)):
                hdr.append(i)
            else:
                for d in self.includeDir:
                    d = os.path.realpath(d)
                    di = os.path.join(d,i)
                    if (os.path.exists(di)):
                        hdr.append(di)
                        break
        return hdr
    
    def _checkIncludeFiles_(self,srcName,hdr):
        needsToBeCompiled = False
        for hdrName in hdr:
            metaFileName = self.objFileName(hdrName) + '.meta'
            self._makeDirectories_(metaFileName)
            lastModTime = int(os.path.getmtime(hdrName))
            if (not os.path.exists(metaFileName)):
                needsToBeCompiled = True
            else: #read in last time of compilation and compare to srcName's mod time
                fin = open(metaFileName,'r')
                lastCompileTime = fin.readline().strip()
                fin.close()
                if (lastCompileTime == ''):
                    lastCompileTime = 0
                lastCompileTime = int(lastCompileTime)
                if (lastModTime > lastCompileTime):
                    needsToBeCompiled = True
            fout = open(metaFileName,'w')
            fout.write(str(lastModTime))
            fout.close()
        return needsToBeCompiled


