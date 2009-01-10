
'''
Add standard Python logging to a class.
'''


from logging import getLogger


class LogMixin():
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._log = getLogger(self.__module__ + '.' + self.__class__.__name__)
        self._debug = self._log.debug
        self._info = self._log.info
        self._warn = self._log.warn
        self._error = self._log.error
        
    def describe(self):
        '''
        This should return a (fairly compact) description of the match.
        '''
        return self.__class__.__name__
