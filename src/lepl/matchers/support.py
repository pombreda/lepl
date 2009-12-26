
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Base classes for matchers.
'''

# pylint: disable-msg=C0103,W0212
# (consistent interfaces)
# pylint: disable-msg=E1101
# (_args create attributes)
# pylint: disable-msg=R0901, R0904, W0142
# lepl conventions

from lepl.core.config import ConfigBuilder
from lepl.support.graph import ArgAsAttributeMixin, PostorderWalkerMixin, \
    ConstructorStr, GraphStr
from lepl.matchers.operators import OperatorMixin, OPERATORS, \
    DefaultNamespace, Matcher
from lepl.core.parser import make_parser, make_matcher
from lepl.support.lib import LogMixin, basestring


class BaseMatcher(ArgAsAttributeMixin, PostorderWalkerMixin, 
                    LogMixin, Matcher):
    '''
    A base class that provides support to all matchers.
    '''
    pass
    
    
class OperatorMatcher(OperatorMixin, BaseMatcher):
    '''
    A base class that provides support to all matchers with operators.
    '''
    
    def __init__(self, name=OPERATORS, namespace=DefaultNamespace):
        super(OperatorMatcher, self).__init__(name=name, namespace=namespace)
        self.config = ConfigBuilder()

    def __str__(self):
        visitor = ConstructorStr()
        return self.postorder(visitor, Matcher)
    
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def tree(self):
        '''
        An ASCII tree for display.
        '''
        visitor = GraphStr()
        return self.postorder(visitor)
    
    def file_parser(self, **kargs):
        '''
        Construct a parser for file objects that uses a stream 
        internally and returns a single result.
        '''
        config = self.config.configuration
        return make_parser(self, config.stream_factory.from_file, config, kargs)
    
    def items_parser(self, **kargs):
        '''
        Construct a parser for a sequence of times (an item is something
        that would be matched by `Any`) that uses a stream internally and 
        returns a single result.
        '''
        config = self.config.configuration
        return make_parser(self, config.stream_factory.from_items, config, kargs) 
    
    def path_parser(self, **kargs):
        '''
        Construct a parser for a file that uses a stream 
        internally and returns a single result.
        '''
        config = self.config.configuration
        return make_parser(self, config.stream_factory.from_path, config, kargs) 
    
    def string_parser(self, **kargs):
        '''
        Construct a parser for strings that uses a stream 
        internally and returns a single result.
        '''
        config = self.config.configuration
        return make_parser(self, config.stream_factory.from_string, config, kargs) 
    
    def null_parser(self, **kargs):
        '''
        Construct a parser for strings and lists that returns a single result
        (this does not use streams).
        '''
        config = self.config.configuration
        return make_parser(self, config.stream_factory.null, config, kargs) 
    
    
    def parse_file(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a single match and using a
        stream internally.
        '''
        return self.file_parser(**kargs)(file_)
        
    def parse_items(self, list_, **kargs):
        '''
        Parse the contents of a sequence of items (an item is something
        that would be matched by `Any`), returning a single match and using a
        stream internally.
        '''
        return self.items_parser(**kargs)(list_)
        
    def parse_path(self, path, **kargs):
        '''
        Parse the contents of a file, returning a single match and using a
        stream internally.
        '''
        return self.path_parser(**kargs)(path)
        
    def parse_string(self, string, **kargs):
        '''
        Parse the contents of a string, returning a single match and using a
        stream internally.
        '''
        return self.string_parser(**kargs)(string)
    
    def parse(self, stream, **kargs):
        '''
        Parse the contents of a string or list, returning a single match (this
        does not use streams).
        '''
        return self.null_parser(**kargs)(stream)
    
    
    def file_matcher(self, **kargs):
        '''
        Construct a parser for file objects that returns a sequence of matches
        and uses a stream internally.
        '''
        config = self.config.configuration
        return make_matcher(self, config.stream_factory.from_file, config, kargs) 
    
    def items_matcher(self, **kargs):
        '''
        Construct a parser for a sequence of items (an item is something that
        would be matched by `Any`) that returns a sequence of matches
        and uses a stream internally.
        '''
        config = self.config.configuration
        return make_matcher(self, config.stream_factory.from_items, config, kargs) 
    
    def path_matcher(self, **kargs):
        '''
        Construct a parser for a file that returns a sequence of matches
        and uses a stream internally.
        '''
        config = self.config.configuration
        return make_matcher(self, config.stream_factory.from_path, config, kargs) 
    
    def string_matcher(self, **kargs):
        '''
        Construct a parser for strings that returns a sequence of matches
        and uses a stream internally.
        '''
        config = self.config.configuration
        return make_matcher(self, config.stream_factory.from_string, config, kargs) 

    def null_matcher(self, **kargs):
        '''
        Construct a parser for strings and lists list objects that returns a 
        sequence of matches (this does not use streams).
        '''
        config = self.config.configuration
        return make_matcher(self, config.stream_factory.null, config, kargs) 

    def match_file(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a sequence of matches and using 
        a stream internally.
        '''
        return self.file_matcher(**kargs)(file_)
        
    def match_items(self, list_, **kargs):
        '''
        Parse a sequence of items (an item is something that would be matched
        by `Any`), returning a sequence of matches and using a
        stream internally.
        '''
        return self.items_matcher(**kargs)(list_)
        
    def match_path(self, path, **kargs):
        '''
        Parse a file, returning a sequence of matches and using a
        stream internally.
        '''
        return self.path_matcher(**kargs)(path)
        
    def match_string(self, string, **kargs):
        '''
        Parse a string, returning a sequence of matches and using a
        stream internally.
        '''
        return self.string_matcher(**kargs)(string)

    def match(self, stream, **kargs):
        '''
        Parse a string or list, returning a sequence of matches 
        (this does not use streams).
        '''
        return self.null_matcher(**kargs)(stream)
    
    
def coerce_(arg, function=None):
    '''
    Many arguments can take a string which is implicitly converted (via this
    function) to a literal (or similar).
    '''
    if function is None:
        from lepl.matchers.core import Literal
        function = Literal
    return function(arg) if isinstance(arg, basestring) else arg


