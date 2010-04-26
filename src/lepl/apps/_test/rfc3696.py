
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
Tests for the lepl.apps.rfc3696 module.
'''

from lepl import *
from lepl._test.base import assert_str, BaseTest
from lepl.apps.rfc3696 import PreferredFullyQualifiedDnsName, EmailLocalPart,\
    Email, HtmlUrl


class DnsNameTest(BaseTest):
    
    def test_dns_name(self):
        
        name = PreferredFullyQualifiedDnsName() & Eos()
        
        self.assert_fail('', name)
        self.assert_fail('a', name)
        self.assert_fail('12.34', name)
        self.assert_fail('a.b.', name)
        self.assert_fail(' a.b', name)
        self.assert_fail('a.b ', name)
        self.assert_fail('a._.', name)
        self.assert_fail('a.-b.c', name)
        self.assert_fail('a.b-.c', name)
        self.assert_fail('a.b.c.123', name)
        
        self.assert_literal('a.b.123.c', name)
        self.assert_literal('a.b-c.d', name)
        self.assert_literal('a.b--c.d', name)
        self.assert_literal('acooke.org', name)
        self.assert_literal('EXAMPLE.COM', name)


class EmailLocalPartTest(BaseTest):
    
    def test_email_local_part(self):
        
        local = EmailLocalPart() & Eos()
        
        self.assert_fail('', local)
        self.assert_fail('""', local)
        self.assert_fail('"unmatched', local)
        self.assert_fail('unmatched"', local)
        self.assert_fail(' ', local)
        self.assert_fail('a b', local)
        
        self.assert_literal(r'andrew', local)
        self.assert_literal(r'Abc\@def', local)
        self.assert_literal(r'Fred\ Bloggs', local)
        self.assert_literal(r'Joe.\\Blow', local)
        self.assert_literal(r'"Abc@def"', local)
        self.assert_literal(r'"Fred Bloggs"', local)
        self.assert_literal(r'user+mailbox', local)
        self.assert_literal(r'customer/department=shipping', local)
        self.assert_literal(r'$A12345', local)
        self.assert_literal(r'!def!xyz%abc', local)
        self.assert_literal(r'_somename', local)


class EmailTest(BaseTest):
    
    def test_email(self):
        
        email = Email() & Eos()
        
        self.assert_literal(r'andrew@acooke.org', email)
        self.assert_literal(r'Abc\@def@example.com', email)
        self.assert_literal(r'Fred\ Bloggs@example.com', email)
        self.assert_literal(r'Joe.\\Blow@example.com', email)
        self.assert_literal(r'"Abc@def"@example.com', email)
        self.assert_literal(r'"Fred Bloggs"@example.com', email)
        self.assert_literal(r'user+mailbox@example.com', email)
        self.assert_literal(r'customer/department=shipping@example.com', email)
        self.assert_literal(r'$A12345@example.com', email)
        self.assert_literal(r'!def!xyz%abc@example.com', email)
        self.assert_literal(r'_somename@example.com', email)
        

class HttpUrl(BaseTest):
    
    def test_http(self):
        
        http = HtmlUrl() & Eos()
        http.config.compile_to_re()
        print(http.get_parse().matcher.tree())
        
        self.assert_literal(r'http://www.acooke.org', http)
        self.assert_literal(r'http://www.acooke.org/', http)
        self.assert_literal(r'http://www.acooke.org:80', http)
        self.assert_literal(r'http://www.acooke.org:80/', http)
        self.assert_literal(r'http://www.acooke.org/andrew', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew', http)
        self.assert_literal(r'http://www.acooke.org/andrew/', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/', http)
        self.assert_literal(r'http://www.acooke.org/?foo', http)
        self.assert_literal(r'http://www.acooke.org:80/?foo', http)
        self.assert_literal(r'http://www.acooke.org/#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew?foo', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew?foo', http)
        self.assert_literal(r'http://www.acooke.org/andrew/?foo', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/?foo', http)
        self.assert_literal(r'http://www.acooke.org/andrew#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew/#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew?foo#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew?foo#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew/?foo#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/?foo#bar', http)
        