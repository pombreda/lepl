from distutils.core import setup

setup(name='LEPL',
      version='4.0',
      description='A Parser Library for Python 2.6+/3+: Recursive Descent; Full Backtracking',
      long_description='''
LEPL is a recursive descent parser, written in Python, which has a a friendly,
easy-to-use syntax.  The underlying implementation includes
several features that make it more powerful than might be expected.

For example, it is not limited by the Python stack, because it uses
trampolining and co-routines.  Multiple parses can be found for ambiguous
grammars and it can also handle left-recursive grammars.

The aim is a powerful, extensible parser that will also give solid, reliable
results to first-time users.

`Release 4.0 <http://www.acooke.org/lepl/lepl4.0.html>`_ is a major revision,
giving a library that's simpler, faster, and eaier to use.

Features
--------

* **Parsers are Python code**, defined in Python itself.  No separate
  grammar is necessary.

* **Friendly syntax** using Python's operators allows grammars
  to be defined in a declarative style close to BNF.

* Integrated, optional **lexer** simplifies handling whitespace.

* Built-in **AST support** with support for iteration, traversal and
  re--writing.

* Generic, pure-Python approach supports parsing a wide variety of data
  including **bytes** (Python 3+ only).

* **Well documented** and easy to extend.

* **Unlimited recursion depth**.  The underlying algorithm is
  recursive descent, which can exhaust the stack for complex grammars
  and large data sets.  LEPL avoids this problem by using Python
  generators as coroutines (aka "trampolining").

* **Parser rewriting**.  The parser can itself be manipulated by
  Python code.  This gives unlimited opportunities for future
  expansion and optimisation.

* Support for ambiguous grammars (**complete backtracking**).  A
  parser can return more than one result (aka **"parse forests"**).

* Parsers can be made more **efficient** with automatic memoisation ("packrat
  parsing").

* Memoisation can detect and control **left-recursive grammars**.  Together
  with LEPL's support for ambiguity this means that "any" grammar can be
  supported.

* Pluggable trace and resource management, including **"deepest match"
  diagnostics** and the ability to limit backtracking.
''',
      author='Andrew Cooke',
      author_email='andrew@acooke.org',
      url='http://www.acooke.org/lepl/',
      packages=['lepl',          'lepl._test',          'lepl._example',
                'lepl.bin',      'lepl.bin._test',      'lepl.bin._example',
                'lepl.contrib',
                'lepl.core',     'lepl.core._test',
                'lepl.lexer',    'lepl.lexer._test',    'lepl.lexer._example',
                'lepl.matchers', 'lepl.matchers._test',
                'lepl.offside',  'lepl.offside._test',  'lepl.offside._example',
                'lepl.regexp',   'lepl.regexp._test',
                'lepl.stream',   'lepl.stream._test',
                'lepl.support',  'lepl.support._test',
                ],
      package_dir = {'':'src'},
      license = "LGPL",
      keywords = "parser",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.0',
                   'Programming Language :: Python :: 3.1',
                   'Programming Language :: Python :: 2.6',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Text Processing',
                   'Topic :: Text Processing :: Filters',
                   'Topic :: Text Processing :: General',
                   'Topic :: Utilities'
                   ]
     )
