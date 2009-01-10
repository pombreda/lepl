 
'''
Central, per-parse repository.
'''

from lepl.resources import GeneratorControl
from lepl.trace import LogMixin
from lepl.support import CircularFifo


class Core():
    '''
    Data store for a single parse; embedded in the streams used to wrap the
    text being parsed.
    '''

    def __init__(self, max_queue=0, description_length=6):
        self.gc = GeneratorControl(max_queue)
        self.description_length = description_length
        