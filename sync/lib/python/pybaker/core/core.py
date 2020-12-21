'''
Created on Nov 19, 2017

@author: 
'''
import os

piesDir = 'pies'
objectFileExt = '.o'

class Compiler(object):
    cmdName = ''
    def __init__(self):
        self.name = ''
        self.ext = []
        self.exclude = []
        
    def compile(self,srcName,projectDir):
        retval = 0
        needsToBeCompiled = False
        objFileName = self.objFileName(srcName,projectDir)
        metaFileName = objFileName + '.meta'
        self.__makeDirectories__(metaFileName)
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
        if (needsToBeCompiled): #compile and write srcName's last mod time to meta file
            #compile file and check that return value is 0
            cmd = self._sourceToObjectCommand_(objFileName,srcName)
            retval = os.system(cmd)
            #if (self.compilerCommand == 'echo'): #this is the do nothing compiler
            #    pass
                #retval = 1
            if (retval == 0):
                fout = open(metaFileName,'w')
                fout.write(str(lastModTime))
                fout.close()
        return retval

    def compileCmd(self,srcName,projectDir):
        needsToBeCompiled = False
        objFileName, xt = self.objectFileName(srcName,projectDir)
        if (not xt in self.ext):
            return '',''
        metaFileName = objFileName + '.meta'
        self.__makeDirectories__(metaFileName)
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
        cmd = ''
        if (needsToBeCompiled): #compile and write srcName's last mod time to meta file
            #compile file and check that return value is 0
            cmd = self._sourceToObjectCommand_(objFileName,srcName)
        return cmd, metaFileName
    
    def __makeDirectories__(self, fileName):
        d = os.path.dirname(fileName)
        if (not os.path.exists(d)):
            os.makedirs(d)
    
    def objFileName(self,srcName,projectDir):
        head,tail = os.path.split(srcName)
        if (not head == '' and not projectDir == ''):
            head = head.split(projectDir)[1]
        if (len(head) > 1 and head[1] == '\\'):
            head = head[2:]
        elif (len(head) > 0 and (head[0] == '\\' or head[0] == '/')):
            head = head[1:]
        dty = os.path.join(projectDir,piesDir)
        objFileName = os.path.join(dty,head,self.name + '-' + tail)
        if ('.' in tail):
            objFileName = objFileName.rsplit('.',1)[0]
        objFileName += objectFileExt
        return objFileName

    def metaFileName(self,srcName,projectDir):
        return self.objFileName(srcName, projectDir) + '.meta'
        
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
        return 'echo build exe'

noSource = '!#dummy#!'

class Target(object):
    def __init__(self,name,compiler,srcName=noSource,sourceDir='',outputDir=''):
        self.target = []
        self._dep = []
        self.name = name
        self.srcName = srcName
        self.compiler = compiler
        self.outputDir = outputDir
        self.sourceDir = sourceDir
        self._callBuild = True
        self.compilerLookup = []
        self.objName = []
        self._cmd = []
        self._meta = []
        self.lastModTime = []

    def build(self):
        self._callBuild = False
        os.chdir(os.getcwd())
        if (not self.sourceDir == ''):
            # self.sourceDir = os.getcwd()
            os.chdir(self.sourceDir)
            self.sourceDir = ''
        if (self.outputDir == ''):
            self.outputDir = self.sourceDir
        if (self.srcName == noSource):
            self.srcName = self.sourceDir
        
        self.compilerLookup.append(self.compiler)
        retTup = self.resolve(self.sourceDir)
        if (not retTup[0] == 0):
            print('Build Error for target: ' + self.name)
            return retTup[0]
        lastModTime = 0
        if (not len(self.lastModTime) == 0):
            lastModTime = max(self.lastModTime)
        metaFileName = self.compiler.metaFileName(self.name, self.sourceDir)
        targetName = os.path.join(self.outputDir,self.name)
        retval = 0
        if (not os.path.exists(metaFileName)):
            cmd = self.compiler._buildCommand_(self.objName,targetName)
            retval = os.system(cmd)
        else: #read in last time of compilation and compare to srcName's mod time
            fin = open(metaFileName,'r')
            lastCompileTime = fin.readline().strip()
            fin.close()
            if (lastCompileTime == ''):
                lastCompileTime = 0
            lastCompileTime = int(lastCompileTime)
            if (lastModTime > lastCompileTime):
                cmd = self.compiler._buildCommand_(self.objName,targetName)
                retval = os.system(cmd)
        fout = open(metaFileName,'w')
        fout.write(str(lastModTime))
        fout.close()
        return retval

    def resolve(self,sourceDir):
        retval = 0
        self.objName = []
        self.lastModTime = []
        self._dep = self.target
        if (self._callBuild):
            retval = self.build()
            #os.chdir(sourceDir)
            os.chdir(os.path.join(os.getcwd(),sourceDir))
        elif (not os.path.exists(os.path.join(os.getcwd(),self.srcName))):
            retval = 1
        elif (os.path.isfile(os.path.join(os.getcwd(),self.srcName))):
            if (self.compiler.name == ''):
                self.__findCompiler__()
            if (not self.compiler.name == ''):
                retval = self.compiler.compile(self.srcName,sourceDir)
                objName = self.compiler.objFileName(self.srcName, sourceDir)
                if (retval == 0):
                    lastModTime = int(os.path.getmtime(self.srcName))
                    self.lastModTime.append(lastModTime)
                    self.objName.append(objName)
        elif (os.path.isdir(os.path.join(os.getcwd(),self.srcName)) and not self.name == piesDir):
            self.__updateDependencies__()
            for d in self._dep:
                retval, subObjName, lastModTime = d.resolve(sourceDir)
                if (retval == 0):
                    self.objName.extend(subObjName)
                    self.lastModTime.extend(lastModTime)
        elif (self.srcName[-3:] == '.py'):
            retval = self.__runBuildFile__()
        return retval, self.objName, self.lastModTime

    def resolvePar(self,sourceDir):
        self.objName = []
        self.lastModTime = []
        self._cmd = []
        self._meta = []
        self._dep = self.target
        if (self._callBuild):
            self.build()
            os.chdir(sourceDir)
        elif (not os.path.exists(self.srcName)):
            self._cmd.append('echo ')
        elif (os.path.isfile(self.srcName)):
            if (self.compiler.name == ''):
                self.__findCompiler__()
            cmd = self.compiler.compileCmd(self.srcName,sourceDir)
            objName = self.compiler.objFileName(self.srcName, sourceDir)
            lastModTime = int(os.path.getmtime(self.srcName))
            self.lastModTime.append(lastModTime)
            self.objName.append(objName)
            self._cmd.append(cmd[0])
            self._meta.append(cmd[1])
        elif (os.path.isdir(self.srcName)):
            if (self.name == piesDir):
                return self._cmd, self._meta, self.objName, self.lastModTime
            self.__updateDependencies__()
            for d in self._dep:
                cmd, meta, subObjName, lastModTime = d.resolvePar(sourceDir)
                self.objName.extend(subObjName)
                self._cmd.extend(cmd)
                self._meta.extend(meta)
                self.lastModTime.extend(lastModTime)
        elif (self.srcName[-3:] == '.py'):
            self._cmd.append('python ' + self.srcName)
            self._meta.append('')
            self.objName.append('')
        return self._cmd, self._meta, self.objName, self.lastModTime

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
        self._dep = []
        for name in rscNames:
            t = Target(name, Compiler(), os.path.join(self.srcName,name))
            t.compilerLookup = self.compilerLookup
            t._callBuild = False
            self._dep.append(t)
        pass

    def __runBuildFile__(self):
        return os.system('python ' + self.srcName)
