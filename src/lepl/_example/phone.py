
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,W0621,R0904
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class PhoneExample(Example):
    
    def test_fragment1(self):
        
        name    = Word()              > 'name'
        matcher = name / ','
        matcher.config.no_full_first_match()
        parser = matcher.get_parse_string()
        self.examples([(lambda: parser('andrew, 3333253'),
                        "[('name', 'andrew'), ',']")])
    
    def test_fragment2(self):
        
        name    = Word()              > 'name'
        phone   = Integer()           > 'phone'
        matcher = name / ',' / phone
        matcher.config.no_full_first_match()
        parser = matcher.get_parse_string()
        self.examples([(lambda: parser('andrew, 3333253'),
                        "[('name', 'andrew'), ',', ' ', ('phone', '3333253')]")])
    
    def test_fragment3(self):
        
        name    = Word()              > 'name'
        matcher = name                > make_dict
        matcher.config.no_full_first_match()
        parser = matcher.get_parse_string()
        self.examples([(lambda: parser('andrew, 3333253'),
                        "[{'name': 'andrew,'}]")])
    
    def test_fragment4(self):
        
        #basicConfig(level=DEBUG)
        
        name    = Word()              > 'name'
        matcher = name / ','          > make_dict
        matcher.config.clear().flatten()
        parser = matcher.get_parse_string()
        #print(repr(parser.matcher))
        matcher.config.clear().flatten().compose_transforms().trace(True)
        parser = matcher.get_parse_string()
        #print(repr(parser.matcher))
        self.examples([(lambda: parser('andrew, 3333253'),
                        "[{'name': 'andrew'}]")])
    
    def test_basic_parser(self):
        
        #basicConfig(level=DEBUG)

        name    = Word()              > 'name'
        phone   = Integer()           > 'phone'
        matcher = name / ',' / phone  > make_dict
        
#        matcher.config.clear()
#        print()
#        print(repr(matcher.get_parse_string().matcher))
#        matcher.config.clear().flatten()
#        print(repr(matcher.get_parse_string().matcher))
#        matcher.config.clear().flatten().compose_transforms()
#        print(repr(matcher.get_parse_string().matcher))
        parser = matcher.get_parse_string()

        self.examples([(lambda: parser('andrew, 3333253'),
                        "[{'phone': '3333253', 'name': 'andrew'}]"),
                       (lambda: matcher.parse_string('andrew, 3333253')[0],
                        "{'phone': '3333253', 'name': 'andrew'}"),
                       (lambda: (name / ',' / phone).parse('andrew, 3333253'),
                        "[('name', 'andrew'), ',', ' ', ('phone', '3333253')]")])


    def test_components(self):
        
        self.examples([(lambda: (Word() > 'name').parse('andrew'),
                        "[('name', 'andrew')]"),
                       (lambda: (Integer() > 'phone').parse('3333253'),
                        "[('phone', '3333253')]"),
                       (lambda: dict([('name', 'andrew'), ('phone', '3333253')]),
                        "{'phone': '3333253', 'name': 'andrew'}")])


    def test_repetition(self):
        
        spaces  = Space()[0:]
        name    = Word()              > 'name'
        phone   = Integer()           > 'phone'
        line    = name / ',' / phone  > make_dict
        newline = spaces & Newline() & spaces
        matcher = line[0:,~newline]
        
        self.examples([(lambda: matcher.parse('andrew, 3333253\n bob, 12345'),
                        "[{'phone': '3333253', 'name': 'andrew'}, {'phone': '12345', 'name': 'bob'}]")])
        
        
    def test_combine(self):
        
        def combine(results):
            all = {}
            for result in results:
                all[result['name']] = result['phone']
            return all
        
        spaces  = Space()[0:]
        name    = Word()              > 'name'
        phone   = Integer()           > 'phone'
        line    = name / ',' / phone  > make_dict
        newline = spaces & Newline() & spaces
        matcher = line[0:,~newline]   > combine
        
        self.examples([(lambda: matcher.parse('andrew, 3333253\n bob, 12345'),
                        "[{'bob': '12345', 'andrew': '3333253'}]")])

    