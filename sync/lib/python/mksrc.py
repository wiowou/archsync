import sys

from mksrctemplate.cpp_header import cppheader
from mksrctemplate.cpp_source import cppsource
from mksrctemplate.cpp_main import cppmain
from mksrctemplate.cpp_sourceTest import cppsourceTest

from mksrctemplate.c_header import cheader
from mksrctemplate.c_source import csource
from mksrctemplate.c_main import cmain
from mksrctemplate.c_sourceTest import csourceTest

class FileType(object):
    def __init__(self):
        self.isHeader=False
        self.isSource=False
        self.isTest=False
        self.isMain=False
        self.isCpp=False
        self.isC=False
        self.isCuda=False
        self.isMain=False
        self.hdrExt=''

name=''
NAME=''
Name=''
headerQualifier=''
qualifier=''
namespaces=''
namespacePrefix=''
Enamespaces=''
hdrExt=''

headerStr=''
sourceStr=''
mainStr=''
sourceTestStr=''
ns=[]

def usage():
    print('mksrc [n1::n2::]name.ext1[,ext2,test]')

def replace(s):
    s = s.replace('${Name}',Name)
    s = s.replace('${NAME}',NAME)
    s = s.replace('${name}',name)
    s = s.replace('${headerQualifier}',headerQualifier)
    s = s.replace('${namespaces}',namespaces)
    s = s.replace('${Enamespaces}',Enamespaces)
    s = s.replace('${hdrExt}',hdrExt)
    s = s.replace('${namespacePrefix}',namespacePrefix)
    return s

def findType(qual,ex):
    ft = FileType()
    for e in ex:
        if e == 'cpp':
            ft.isCpp=True
            ft.isSource=True
        elif e == 'cu':
            ft.isCuda=True
            ft.isSource=True
        elif e == 'c':
            ft.isC=True
            ft.isSource=True
        elif e == 'hpp':
            ft.isCpp=True
            ft.isHeader=True
            ft.hdrExt=e
        elif e == 'cuh':
            ft.isCuda=True
            ft.isHeader=True
            ft.hdrExt=e
        elif e == 'h' and '::' in qual:
            ft.isCpp=True
            ft.isHeader=True
            ft.hdrExt=e
        elif e == 'h':
            ft.isC=True
            ft.isHeader=True
            ft.hdrExt=e
        elif e == 'test':
            ft.isTest=True
    return ft
            
def write(ft):
    if ft.isCpp:
        if ft.isHeader:
            f = open(name+'.'+hdrExt,'w')
            f.write(headerStr)
            f.close()
        if ft.isSource:
            f = open(name+'.cpp','w')
            f.write(sourceStr)
            f.close()
        if ft.isTest:
            f = open('../UnitTests/'+name+'Test.cpp','w')
            f.write(sourceTestStr)
            f.close()
        if ft.isMain:
            f = open('main.cpp','w')
            f.write(mainStr)
            f.close()
    elif ft.isCuda:
        if ft.isHeader:
            f = open(name+'.'+hdrExt,'w')
            f.write(headerStr)
            f.close()
        if ft.isSource:
            f = open(name+'.cu','w')
            f.write(sourceStr)
            f.close()
        if ft.isTest:
            f = open('../UnitTests/'+name+'Test.cu','w')
            f.write(sourceTestStr)
            f.close()
        if ft.isMain:
            f = open('main.cu','w')
            f.write(mainStr)
            f.close()
    elif ft.isC:
        if ft.isHeader:
            f = open(name+'.'+hdrExt,'w')
            f.write(headerStr)
            f.close()
        if ft.isSource:
            f = open(name+'.c','w')
            f.write(sourceStr)
            f.close()
        if ft.isTest:
            f = open('../UnitTests/'+name+'.c','w')
            f.write(sourceTestStr)
            f.close()
        if ft.isMain:
            f = open('main.c','w')
            f.write(mainStr)
            f.close()

if __name__ == '__main__':
    if (not len(sys.argv) == 2 or sys.argv[1] == '-h' or sys.argv[1] == '-help' or not '.' in sys.argv[1]):
        usage()
        sys.exit(1)
    qualifier,ext = sys.argv[1].split('.')
    ext = ext.split(',')
    ft = findType(qualifier,ext)
    if ft.isCpp:
        headerStr=cppheader
        sourceStr=cppsource
        mainStr=cppmain
        sourceTestStr=cppsourceTest
        name = qualifier
        if ('::' in qualifier):
            ns = qualifier.split('::')
            name = ns[-1]
        for n in ns[:-1]:
            namespaces += 'namespace ' + n + '{\n'
            namespacePrefix += n + "::"
            headerQualifier += n.upper()
        for n in ns[1::-1]:
            Enamespaces += '}/*' + n + '*/'
        hdrExt=ft.hdrExt
    elif ft.isC:
        hdrExt='h'
        name = qualifier
        headerStr=cheader
        sourceStr=csource
        mainStr=cmain
        sourceTestStr=csourceTest
    elif ft.isCuda:
        hdrExt='cuh'
        name = qualifier
        headerStr=cheader
        sourceStr=csource
        mainStr=cmain
        sourceTestStr=csourceTest
    Name = name[0].upper() + name[1:]
    NAME = name.upper()
    headerStr = replace(headerStr)
    sourceStr = replace(sourceStr)
    mainStr = replace(mainStr)
    sourceTestStr = replace(sourceTestStr)
    if (name == 'main' ):
            ft.isMain=True
    write(ft)
    
    