try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='LEPL',
      version='2.0',
      description='A Parser Library for Python 3 (and 2.6): Recursive Descent; Full Backtracking',
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
