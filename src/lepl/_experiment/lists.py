
# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.


'''
I'm considering replacing Node with something simpler, based on lists.

Node was never designed - it's a hack built on classes that already existed.
Subclassing list is much simpler, making it easier to use and understand.

Of course, Node would still exist, but all examples would switch to lists,
and that would be considered the default for future work.
'''

from functools import reduce

from lepl import *
from lepl.support.lib import lmap, fmt

class List(list):
    '''
    Extend a list with AST related utilities.
    '''
    
    def tree(self):
        return list_to_tree(self)
    
    def __repr__(self):
        return self.__class__.__name__ + '(...)'
    
    def __str__(self):
        return list_to_str(self)
    

def make_fold(per_list=None, per_item=None, 
              exclude=lambda x: isinstance(x, str)):
    '''
    We need some kind of fold-like procedure for generalising operations on
    arbitrarily nested iterables.  We can't use a normal fold because Python
    doesn't have the equivalent of cons, etc.  Instead, to be Pythonic, we
    use iterators.  This is made up - there's no theoretical basis to it,
    it just looks about right / general enough.
    
    We divide everything into iterables ("lists") and atomic values ("items").
    per_list is called with a iterator the top-most list, in order.  Items 
    (ie atomic values) in that list, when requested from the iterator, will 
    be processed by per_item; iterables will be processed by a separate call
    to per_list.
    '''
    if per_list is None:
        per_list = lambda type_, items: type_(items)
    if per_item is None:
        per_item = lambda x: x
    def items(iterable):
        for item in iterable:
            try:
                if not exclude(item):
                    yield per_list(type(item), items(iter(item)))
                    continue
            except Exception:
                pass
            yield per_item(item)
    return lambda list_: per_list(type(list_), items(list_))

## These need to be turned into tests
#
#clone = make_fold()
#
#print(clone([]))
#print(clone([1,2,3]))
#print(clone([[1],2,3]))
#print(clone([[[1]],2,3]))
#print(clone([[[1]],2,[3]]))
#print(clone([[[1]],'2',[3]]))
#
#count = make_fold(per_list=lambda type_, items: sum(items), 
#                  per_item=lambda item: 1)
#
#print(count([]))
#print(count([1,2,3]))
#print(count([[1],2,3]))
#print(count([[[1,2],3],4,5]))
#
#join_list = lambda items: reduce(lambda x, y: x+y, items, [])
#flatten = make_fold(per_list=lambda type_, items: join_list(items),
#                    per_item=lambda item: [item])
#
#print(flatten([]))
#print(flatten([1,2,3]))
#print(flatten([[1],2,3]))
#print(flatten([[[1,2],3],4,5]))
#
#'''
#This need adapting to use higher order functions to all the neat fmtting,
#but shows the basic idea.
#'''
##list_to_tree = \
##    lambda list_: \
##        '\n'.join(make_fold(per_list=lambda type_, items: join_list(lmap(lambda item: lmap(lambda x: ' ' + x, item), items)), 
##                            per_item=lambda item: [str(item)])(list_))
#        
#list_to_str = make_fold(per_list=lambda type_, items: 
#                            fmt('{0}({1})', type_.__name__, ','.join(items)), 
#                        per_item=lambda item: repr(item))

def list_to_tree(list_):
    '''
    Generate a tree using the same "trick" as `GraphStr`.
    
    The initial fold returns a function (str, str) -> list(str) at each
    level.
    '''
    def per_item(item):
        def fun(first, _rest):
            return [first + str(item)]
        return fun
    def per_list(type_, list_):
        def fun(first, rest):
            yield [first + str(type_.__name__)]
            force = list(list_) # need to access last item explicitly
            for item in force[:-1]:
                yield item(rest + ' +- ', rest + ' |  ')
            yield force[-1](rest + ' `- ', rest + '    ')
        return lambda first, rest: join_list(list(fun(first, rest)))
    fold = make_fold(per_list, per_item)
    return '\n'.join(fold(list_)('', ''))

#class Term(List): pass
#class Factor(List): pass
#class Expression(List): pass
#    
#expr   = Delayed()
#number = Digit()[1:,...]                         >> int
#
#with Separator(Drop(Regexp(r'\s*'))):
#    term    = number | '(' & expr & ')'          > Term
#    muldiv  = Any('*/')
#    factor  = term & (muldiv & term)[:]          > Factor
#    addsub  = Any('+-')
#    expr   += factor & (addsub & factor)[:]      > Expression
#    line    = expr & Eos()
#    
#ast = line.parse_string('1 + 2 * (3 + 4 - 5)')[0]
#
#print(ast)
## Expression(Factor(Term(1)),'+',Factor(Term(2),'*',Term('(',Expression(Factor(Term(3)),'+',Factor(Term(4)),'-',Factor(Term(5))),')')))
#print(repr(ast))
##   1
## +
##   2
##  *
##   (
##      3
##    +
##      4
##    -
##      5
##   )
#print(ast.tree())

