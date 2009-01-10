

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
    

class SelfDocumentingGenerator():
    '''
    Add logging info to generators.
    '''
    
    def __init__(self, generator, logMixin, stream):
        self.__generator = generator
        self.__owner = logMixin
        self.__tag = '%s@%s' % (self.__owner.describe(), stream)
        self.__owner._debug('Opening %s' % self)
        
    def __next__(self):
        self.__owner._debug('Reading %s' % self)
        return next(self.__generator)
    
    def __iter__(self):
        return self
    
    def close(self):
        self.__owner._debug('Ckosing %s' % self)
        self.__generator.close()
    
    def __str__(self):
        return self.__tag


