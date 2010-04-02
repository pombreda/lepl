
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
Performance related tests.
'''

# pylint: disable-msg=C0103, C0111, C0301, W0702, C0324, C0102, C0321, W0141, W0614, W0401, R0914, R0903
#@PydevCodeAnalysisIgnore


from logging import basicConfig, DEBUG

from lepl import *
from lepl.core.trace import StreamMonitor


def natural_language():
    '''
    This focuses on the LMemo cache.  It does not use any monitor or stream.
    '''
    
    basicConfig(level=DEBUG)
    
    class VerbPhrase(Node): pass
    class DetPhrase(Node): pass
    class SimpleTp(Node): pass
    class TermPhrase(Node): pass
    class Sentence(Node): pass
    
    verb        = Literals('knows', 'respects', 'loves')         > 'verb'
    join        = Literals('and', 'or')                          > 'join'
    proper_noun = Literals('helen', 'john', 'pat')               > 'proper_noun'
    determiner  = Literals('every', 'some')                      > 'determiner'
    noun        = Literals('boy', 'girl', 'man', 'woman')        > 'noun'
    
    verbphrase  = Delayed()
    verbphrase += verb | (verbphrase // join // verbphrase)      > VerbPhrase
    det_phrase  = determiner // noun                             > DetPhrase
    simple_tp   = proper_noun | det_phrase                       > SimpleTp
    termphrase  = Delayed()
    termphrase += simple_tp | (termphrase // join // termphrase) > TermPhrase
    sentence    = termphrase // verbphrase // termphrase & Eos() > Sentence

    sentence.config.auto_memoize().no_full_first_match()
    sentence.config.add_monitor(StreamMonitor)
    p = sentence.get_match_string()
    print(repr(p.matcher))
    #for _i in range(100):
    for _i in range(1):
        assert len(list(p('every boy or some girl and helen and john or pat knows '
                          'and respects or loves every boy or some girl and pat or '
                          'john and helen'))) == 392  


def natural_language2():
    '''
    This focuses on the LMemo cache.  It does not use any monitor or stream.
    '''
    
    #basicConfig(level=DEBUG)
    
    class VerbPhrase(Node): pass
    class DetPhrase(Node): pass
    class SimpleTp(Node): pass
    class TermPhrase(Node): pass
    class Sentence(Node): pass
    
    t           = Token('[a-z]+')
    
    verb        = t(Literals('knows', 'respects', 'loves'))    > 'verb'
    join        = t(Literals('and', 'or'))                     > 'join'
    proper_noun = t(Literals('helen', 'john', 'pat'))          > 'proper_noun'
    determiner  = t(Literals('every', 'some'))                 > 'determiner'
    noun        = t(Literals('boy', 'girl', 'man', 'woman'))   > 'noun'
    
    verbphrase  = Delayed()
    verbphrase += verb | (verbphrase & join & verbphrase)      > VerbPhrase
    det_phrase  = determiner & noun                            > DetPhrase
    simple_tp   = proper_noun | det_phrase                     > SimpleTp
    termphrase  = Delayed()
    termphrase += simple_tp | (termphrase & join & termphrase) > TermPhrase
    sentence    = termphrase & verbphrase & termphrase & Eos() > Sentence

    sentence.config.auto_memoize(full=True)
    #sentence.config.add_monitor(StreamMonitor)
    p = sentence.get_match_string()
    print(repr(p.matcher))
    for _i in range(100):
        assert len(list(p('every boy or some girl and helen and john or pat knows '
                          'and respects or loves every boy or some girl and pat or '
                          'john and helen'))) == 392  


def time():
    from timeit import Timer
    t = Timer("natural_language2()", "from __main__ import natural_language2")
    print(t.timeit(number=1))
    # without compilation, and with smart dfa switch:
    # with dfa: 12.4
    # without dfa: 5.7
    # default: 12.4
    # with tokens: 13.3
    
    # all numbers below included compilation!
    # using LMemo:
    # 6.3, 6.6 for 2.0 on laptop
    # 5.3 after simplifying generator wrapper
    # using auto_memoize 48 -> 34 (44->31)
    # Or as Transformable -> 24
    # RMemo as Transformable -> 30
    # Both as Transformable -> 27
    # So not worth making RMemo transformable(!)
    # Seem to be back at 27 for auto_memoize(False) after fixing bugs
    # and slightly worse (28) for auto_memoize(True)
    # DFA (and so NFA) makes things slower (40)
    # (expected - converting literal to FSA)
    
    # new code (4.0), count reduced to 100
    # stream - null 42, string 28, null full 2, string full 58
    # tokens - null 14, string 25, null full 5, string full 22
    #          null full no direct 5, string full no direct 30
    #          back to 1000, null full 46 (so it's not caching the whole text)
    # after revising hashes/eq
    # stream - null 5, string 6, null full 3, string full 3
    # tokens - null 12, string 32, null full 5, string full 5
    

def profile():
    '''
import pstats
p=pstats.Stats('nat_lang.prof')
p.strip_dirs()
p.sort_stats('cumulative')
p.sort_stats('time')
p.print_stats(35)
    '''
    import cProfile
    cProfile.run('natural_language()', 'nat_lang.prof')

if __name__ == '__main__':
#    time()
#    profile()
    natural_language()
