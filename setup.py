try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='LEPL',
      version='2.0.2',
      description='A Parser Library for Python 3 (and 2.6): Recursive Descent; Full Backtracking',
      long_description='''
Introducing version 2.0 of LEPL with a new, more powerful core.

I am trying to keep LEPL simple and intuitive while making it easier to add
features from recent research papers "under the hood".  The combination of
trampolining (which exposes the inner loop) and matcher graph rewriting (which
allows the parser to be restructured programmatically) should allow further
extensions without changing the original, simple grammar syntax.

The aim is a powerful, extensible parser that will also give solid, reliable
results to first--time users.  This release is a major step towards that goal.


Features
--------

* **Parsers are Python code**, defined in Python itself.  No separate
  grammar is necessary.

* **Friendly syntax** using Python's operators.

* Built-in **AST support** (a generic Node class).  Improved
  support for the visitor pattern and tree re--writing.

* **Well documented** and easy to extend.

* **Unlimited recursion depth**.  The underlying algorithm is
  recursive descent, which can exhaust the stack for complex grammars
  and large data sets.  LEPL avoids this problem by using Python
  generators as coroutines (aka "trampolining").

* Support for ambiguous grammars (**complete backtracking**).  A
  parser can return more than one result (aka **"parse forests"**).

* **Packrat parsing**.  Parsers can be made much more efficient with
  automatic memoisation.

* **Parser rewriting**.  The parser can itself be manipulated by
  Python code.  This gives unlimited opportunities for future
  expansion and optimisation.

* **Left recursive grammars**.  Memoisation can detect and control
  left--recursive grammars.  Together with LEPL's support for
  ambiguity this means that "any" grammar can be supported.

* Pluggable trace and resource management, including **"deepest match"
  diagnostics** and the ability to limit backtracking.

LEPL's *weakest* point is probably performance.  This has improved
with memoisation, but it is still more suited for exploratory and
one--off jobs than, for example, a compiler front--end.  Measuring and
improving performance is the main target of the next release.
''',
      author='Andrew Cooke',
      author_email='andrew@acooke.org',
      url='http://www.acooke.org/lepl/',
      packages=['lepl'],
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
