import os

piesDir = '.pies'
objectFileExt = '.o'
if (os.name == 'nt'):
    piesDir = piesDir[1:]
    objectFileExt = '.obj'
noSource = '!#dummy#!'
spChar = ' '

from .compiler import Compiler
from .job import Job
from .target import Target
