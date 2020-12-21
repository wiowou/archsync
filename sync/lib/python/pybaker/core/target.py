'''
Created on Nov 19, 2017

@author: 
'''
import os
from multiprocessing import Pool
from pybaker.core import piesDir
from pybaker.core import spChar
from pybaker.core import objectFileExt
from pybaker.core import noSource
from pybaker.core import Compiler

class Target(object):
    def __init__(self,name,compiler,srcName=noSource,sourceDir='',outputDir='',makeFileName='',numproc=1):
        self.target = []
        self._dep = []
        self.name = name
        self.makefileName = makeFileName
        self.srcName = srcName
        self.compiler = compiler
        self.outputDir = outputDir
        self.sourceDir = sourceDir
        self._callBuild = True
        self.compilerLookup = []
        self.objName = []
        self.cmd = []
        self.mkfile = []
        self.lastModTime = []
        self.numproc = numproc
        self.excludeDir = []
        self._owd = os.getcwd()
        for t in self.target:
            t._owd = self._owd

    def build(self,numproc=1):
        os.chdir(self._owd)
        global spChar
        self._callBuild = False
        if (not self.sourceDir == ''):
            os.chdir(self.sourceDir)
        if (self.srcName == noSource):
            self.srcName = ''
                
        if (not self.compiler.name == 'job-compiler'):
            mkentry = piesDir + ' : \n'
            mkentry += '\t' + 'mkdir ' + piesDir + '\n'
            self.mkfile.append(mkentry)
            self.compilerLookup.append(self.compiler)
            retTup = self.resolve(self.makefileName)
            if (not retTup[0] == 0):
                print('   ' + self.name + max(1,(60-len(self.name)))*spChar + '[ERROR-Building]')
                if (spChar == ' '):
                    spChar = '.'
                else:
                    spChar = ' '
                os.chdir(self._owd)
                return retTup[0]
        targetName = os.path.join(self.outputDir,self.name)
        targetName = os.path.realpath(targetName)
        name = self.name
        if (os.name == 'nt'):
            name += '.exe'
        objName = self.compiler.objFileName(name)
        lastModTime = 0
        lastCompileTime = -1
        if (os.path.exists(targetName)):
            lastCompileTime = int(os.path.getmtime(targetName))
        if (not len(self.lastModTime) == 0):
            lastModTime = max(self.lastModTime)
        self.lastModTime.append(lastModTime)
        
        retval = 0
        cmd = self.compiler._buildCommand_(self.objName,targetName)
        needsToBeCompiled = lastModTime > lastCompileTime
        if (not self.compiler.name == 'job-compiler'):
            depStr = piesDir
            for d in self.objName:
                depStr += ' ' + d
            mkentry = targetName + ' : ' + depStr + '\n'
            mkentry += '\t' + cmd + '\n'
            self.mkfile.append(mkentry)
        else:
            if (needsToBeCompiled):
                retval = self.compiler._run_()
                cmd = '[RUN]'
            else:
                cmd = '[UP-TO-DATE]'
            self.compiler._makeDirectories_(objName+'.meta')
            
        if (not needsToBeCompiled):
            cmd = '[UP-TO-DATE]'
        if (not cmd == 'echo buildCommand' and 'exe' in self.compiler.name):
            self.cmd.append(cmd)
            self.objName.append(objName)
        if (not self.compiler.name == 'job-compiler' and not self.makefileName == ''):
            self._writeMakefile_()
        if (self.numproc < 2):
            for i in range(0,len(self.cmd)):
                retval = self._evalCmd_(i)
                if (not retval == 0):
                    break
        else:
            p = Pool(self.numproc)
            retval = p.map(self._evalCmd_, range(0,len(self.cmd)-1))
            retval = max(retval)
            if (retval == 0):
                self._evalCmd_(len(self.cmd)-1)
        os.chdir(self._owd)
        return retval

    def _evalCmd_(self,i):
        global spChar
        targName = self.objName[i][len(piesDir)+1:-len(objectFileExt)]
        retval = 0
        if ('[RUN]' in self.cmd[i]):
            pass
        elif (not '[UP-TO-DATE]' in self.cmd[i]):
            print('   ' + targName + max(1,(60-len(targName)))*spChar + '[BUILDING]')
            if (spChar == ' '):
                spChar = '.'
            else:
                spChar = ' '
            retval = os.system(self.cmd[i])
        else:
            print('   ' + targName + max(1,(60-len(targName)))*spChar + '[UP-TO-DATE]')
            if (spChar == ' '):
                spChar = '.'
            else:
                spChar = ' '
        if (retval == 0):
            metaFileName = self.objName[i]+'.meta'
            metaFileName = os.path.realpath(metaFileName)
            self.compiler._makeDirectories_(metaFileName)
            fout = open(metaFileName,'w')
            fout.write(str(self.lastModTime[i]))
            fout.close()
        else:
            print('   ' + targName + max(1,(60-len(targName)))*spChar + '[ERROR-Building]')
            if (spChar == ' '):
                spChar = '.'
            else:
                spChar = ' '
        return retval

    def resolve(self,makefileName):
        retval = 0
        self.objName = []
        self.lastModTime = []
        if (self._callBuild):
            cwd = os.getcwd()
            retval = self.build()
            os.chdir(cwd)
        elif (not os.path.exists(os.path.join(os.getcwd(),self.srcName))):
            retval = 1
        elif (os.path.isfile(os.path.join(os.getcwd(),self.srcName))):
            if (self.compiler.name == ''):
                self.__findCompiler__()
            if (not self.compiler.name == ''):
                hdrDep = self.compiler.headerDep(self.srcName)
                cmd = self.compiler.compileCmd(self.srcName)
                objName = self.compiler.objFileName(self.srcName)
                depStr = objName + ' : ' + piesDir + ' ' + self.srcName
                for h in hdrDep:
                    depStr += ' ' + h                
                mkentry = depStr + '\n'
                mkentry += '\t' + cmd + '\n'
                self.mkfile.append(mkentry)
                #retval = self.compiler.compile(self.srcName,hdrDep)
                needsToBeCompiled = self.compiler.needsCompilation(self.srcName,hdrDep)
                if (not needsToBeCompiled):
                    cmd = '[UP-TO-DATE]'
                lastModTime = int(os.path.getmtime(self.srcName))
                self.lastModTime.append(lastModTime)
                self.objName.append(objName)
                self.cmd.append(cmd)
        elif (os.path.isdir(os.path.join(os.getcwd(),self.srcName)) and not self.name == piesDir and not self.name in self.excludeDir):
            self.__updateDependencies__()
            for d in self._dep:
                retval, subObjName, lastModTime, cmd, kfile = d.resolve(makefileName)
                if (retval == 0):
                    self.objName.extend(subObjName)
                    self.lastModTime.extend(lastModTime)
                    self.cmd.extend(cmd)
                    self.mkfile.extend(kfile)
        elif (self.srcName[-3:] == '.py'):
            retval = self.__runBuildFile__()
        return retval, self.objName, self.lastModTime, self.cmd, self.mkfile
    
    def _writeMakefile_(self):
        makefile = open(self.makefileName, 'w')
        self.mkfile.insert(0,self.mkfile.pop(len(self.mkfile)-1))
        for line in self.mkfile:
            makefile.write(line)
        makefile.close()

    def specifyCompiler(self,compiler,recurse=False):
        self.compiler = compiler
        if (recurse):
            for d in self._dep:
                d.specifyCompiler(compiler,recurse)
        pass

    def __findCompiler__(self,recurse=False):
        for c in self.compilerLookup:
            if (c.isMatch(self.srcName)):
                self.compiler = c
                break
        if (recurse):
            for d in self._dep.values():
                d.__findCompiler__(recurse)
        pass

    def __updateDependencies__(self):
        rscNames = os.listdir(os.path.join(os.getcwd(),self.srcName))
        self._dep = self.target
        for name in rscNames:
            t = Target(name, Compiler(), os.path.join(self.srcName,name))
            t.compilerLookup = self.compilerLookup
            t._callBuild = False
            self._dep.append(t)
        pass

    def __runBuildFile__(self):
        return os.system('python ' + self.srcName)

