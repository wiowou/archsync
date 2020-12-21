'''
Created on Feb 6, 2018

@author: bk
'''
from pybaker.core import Compiler

class Job(Compiler):
    def __init__(self):
        Compiler.__init__(self)
        self.task = [] #a list of user defined functions
        self.name = 'job-compiler'
        self.id = ''

    def _run_(self):
        retval = 0
        n = 0
        for t in self.task:
            retval = t();
            if (not retval == 0):
                print('Failed running job ' + self.id + 'task ' + str(n) + '\n')
            n += 1
        return retval