#!/usr/local/bin/python3.0

from setuptools import setup, find_packages

setup(name='LEPL',
      version='0.1b2',
      description='A Parser Library for Python 3 (and 2.6): Recursive Descent; Full Backtracking',
      author='Andrew Cooke',
      author_email='andrew@acooke.org',
      url='http://www.acooke.org/lepl/',
      packages=find_packages('src', exclude=['*._test', '*._example']),
      package_dir = {'':'src'},
      license = "LGPL",
      keywords = "parser",
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
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
