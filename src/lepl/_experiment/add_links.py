
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
Remove API Links from the documentation.

This replaces each 
 `.config.lexer() <api/redirect.html#lepl.core.config.ConfigBuilder.lexer>`_
with
 ``.config.lexer()``
'''

from os import walk, rename, remove, fdopen
from os.path import join, exists
from string import ascii_uppercase, ascii_lowercase, digits
from tempfile import mkstemp

import lepl.matchers.support, lepl.bin, lepl, lepl.contrib.json, \
    lepl.apps.rfc3696, lepl.lexer.lexer, lepl.support.graph, \
    lepl.core.rewriters
from lepl.support.lib import fmt
from lepl import *


def print_unknown(name):
    print('No link for:', name)
    return name


def lookup_function(name):
    short = name
    if short.endswith('()'):
        short = short[:-2]
    # handle constants directly
    if short in ['BREADTH_FIRST', 'DEPTH_FIRST', 'GREEDY', 'NON_GREEDY']:
        link = fmt('`{0} <api/redirect.html#lepl.matchers.operators.{1}>`_', name, short)
        #print(name, link)
        return link
    for module in [lepl, lepl.bin, lepl.matchers.support, lepl.contrib.json, 
                   lepl.apps.rfc3696, lepl.lexer.lexer, lepl.support.graph,
                   lepl.core.rewriters]:
        if hasattr(module, short):
            found = getattr(module, short)
            if hasattr(found, '__module__'):
                link = fmt('`{0} <api/redirect.html#{1}.{2}>`_', name, found.__module__, short)
                #print(name, link)
                return link
    raise StopIteration


def lookup_config(name):
    # fix 'config...' to be '.config...'
    if not name.startswith('.'):
        name = '.' + name
    short = name
    if short.endswith('()'):
        short = short[:-2]
    short = short[len('.config.'):]
    if short in ['trace', 'blocks', 'offside']:
        raise StopIteration
    link = fmt('`{0} <api/redirect.html#lepl.core.config.ConfigBuilder.{1}>`_', name, short)
    #print(name, link)
    return link
        

def lookup_parse(name):
    short = name
    # allow prefixes like "matcher."
    index = short.rfind('.')
    if index > -1:
        short = short[index+1:]
    if short.endswith('()'):
        short = short[:-2]
    link = fmt('`{0} <api/redirect.html#lepl.core.config.ParserMixin.{1}>`_', name, short)
    #print(name, link)
    return link


def lookup_module(name):
    try:
        __import__(name)
        link = fmt('`{0} <api/redirect.html#{1}>`_', name, name)
        print(name, link)
        return link
    except:
        raise StopIteration()
        

def matcher():
    
    BQ = '`'
    BQ2 = BQ + BQ
    unquote = Literal(BQ2) >> (lambda x: BQ)
    
    junk = AnyBut(BQ)[1:,...]
    
    function = Assert(Drop(BQ2) + Any(ascii_uppercase + ascii_lowercase + digits + '_.')[1:,...] + Optional('()') + Drop(BQ2) >> lookup_function)
    config = Assert(Drop(BQ2) + Optional('.') + 'config.' + Any(ascii_uppercase + ascii_lowercase + digits + '_.')[1:,...] + Optional('()') + Drop(BQ2) >> lookup_config)
    parse = Assert(Drop(BQ2) + Optional(Any(ascii_lowercase)[1:,...] + '.') + Optional('get_') + Or('parse', 'match') + Optional('_' + Or('string', 'file', 'list', 'iterable', 'sequence')) + Optional('_all') + Optional('()') + Drop(BQ2) >> lookup_parse)
    module = Assert(Drop(BQ2) + 'lepl' + Optional('.' + Any(ascii_lowercase)[1:,...][1:,'.',...]) + Drop(BQ2) >> lookup_module)
    
    unknown = BQ2 + Any(ascii_uppercase + ascii_lowercase + digits + '_.')[1:,...] + Optional('()') + BQ2 >> print_unknown
    
    other = Or(BQ + junk + BQ, BQ2 + junk + BQ2)
    
    return Iterate(junk | config | parse | module | function | unknown | other)


def rst_files():
    for root, dirs, files in walk('/home/andrew/projects/personal/lepl/lepl-hg/doc-src'):
        for file in files:
            if file.endswith('.rst') and '#' not in file:
                yield (join(root, file), root)


def rewrite(matcher, path, dir=None, backup='.old', update=True):
    matcher.config.no_full_first_match().low_memory()
    parser = matcher.get_parse_file_all()
    if update:
        (fd, temp) = mkstemp(dir=dir)
        output = fdopen(fd, 'w')
    with open(path) as input:
        for line in parser(input):
            if update:
                output.write(line[0])
    if update:
        output.close()
        if backup:
            prev = path+backup
            if exists(prev):
                remove(prev)
            rename(path, prev)
        else:
            remove(path)
        rename(temp, path)


def main():
    singleton = matcher()
    for (path, dir) in rst_files():
        if exists(path + '.old'):
            print('!', path)
        else:
            print(path)
            rewrite(singleton, path, dir=dir)
        
        
if __name__ == '__main__':
    main()
    