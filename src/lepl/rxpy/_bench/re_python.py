#LICENCE

import re

class Re(object):

    (I, M, S, U, X,
     IGNORECASE, MULTILINE, DOTALL, UNICODE, VERBOSE) = \
        (re.I, re.M, re.S, re.U, re.X, 
         re.IGNORECASE, re.MULTILINE, re.DOTALL, re.UNICODE, re.VERBOSE)
    
    def __init__(self):
        self.compile = re.compile
#        self.RegexObject = re.RegexObject
#        self.MatchIterator = re.MatchIterator
        self.match = re.match    
        self.search = re.search
        self.findall = re.findall
        self.finditer = re.finditer    
        self.sub = re.sub    
        self.subn = re.subn    
        self.split = re.split    
        self.error = re.error
        self.escape = re.escape    
        self.Scanner = re.Scanner
        
    def __str__(self):
        return 'Python re'
        

_re = Re()
