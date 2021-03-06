
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
Matchers that interact with monitors.
'''

from lepl.matchers.core import OperatorMatcher
from lepl.core.trace import _TraceStack
from lepl.core.parser import tagged


# pylint: disable-msg=E1101, W0212
class Trace(OperatorMatcher):
    '''
    Enable trace logging for the sub-matcher.
    '''
    
    def __init__(self, matcher, trace=True):
        super(Trace, self).__init__()
        self._arg(matcher=matcher)
        self._karg(trace=trace)
        self.monitor_class = _TraceStack

    @tagged
    def _match(self, stream):
        '''
        Attempt to match the stream.
        '''
        try:
            generator = self.matcher._match(stream)
            while True:
                yield (yield generator)
        except StopIteration:
            pass
        
    def on_push(self, monitor):
        '''
        On entering, switch monitor on.
        '''
        monitor.switch(1 if self.trace else -1)
        
    def on_pop(self, monitor):
        '''
        On leaving, switch monitor off.
        '''
        monitor.switch(-1 if self.trace else 1)
        
    
