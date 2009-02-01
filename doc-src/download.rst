
.. _install:


Download And Installation
=========================

.. warning::

  This is the very first release.  So there may be a bug or two.
  Please let me know at andrew@acooke.org.


LEPL is only available for Python 3 and 2.6.  See :ref:`versions` for more
information.

There are several ways to install LEPL --- they are described below, simplest
first.  If you want a local copy of the manual you should also read the
:ref:`localdocs` section.


Install with Setuptools / easy_install (Python 2.6)
---------------------------------------------------

This currently only works for Python 2.6

If you have `setuptools <http://pypi.python.org/pypi/setuptools>`_ installed
you should be able to install LEPL using::

  easy_install lepl

That's it.  There is no need to download anything beforehand;
``easy_install`` will do all the work.


Install with Distutils / setup.py (Python 3 and 2.6)
----------------------------------------------------

Download and unpack a source package (see :ref:`download`) then run::

  python setup.py install

For example, on Gnu/Linux (in the instructions below, "LEPL-xxx" would be
"LEPL-\ |release|\ " for the current release)::

  wget http://lepl.googlecode.com/files/LEPL-xxx.tar.gz
  tar xvfz LEPL-xxx.tar.gz
  cd LEPL-xxx
  python setup.py install


Manual Install (experts only)
-----------------------------

Download and unpack a source package (see :ref:`download`) then add to your
``PYTHONPATH`` or ``site-packages``.


Package Removal (experts only)
------------------------------

If you use setuptools or distutils you do not need to remove an old version
before updating.

To completely remove LEPL from your system, you first need to find where it is
installed.  For example::

  >>> import lepl
  >>> lepl.__file__
  '/usr/local/lib64/python2.6/site-packages/LEPL-1.0b3-py2.6.egg/lepl/__init__.pyc'

You can then delete the appropriate file or directory (in the example above,
that would be
``/usr/local/lib64/python2.6/site-packages/LEPL-1.0b3-py2.6.egg``).



.. _localdocs:

Documentation
-------------

You are curently reading the `Manual <http://www.acooke.org/lepl>`_.  The `API
Documentation <http://www.acooke.org/lepl/api>`_ is also available.

The simplest way to view the documentation is via the `web
<http://www.acooke.org/lepl>`_.  However, you can also install a local copy.
Simply download and unpack the appropriate files (see :ref:`download`, below).


.. _download:

Download
--------

You can download the source and documentation packages from the `Support Site
<http://code.google.com/p/lepl/downloads>`_.

The source packages are also available from the `Python Package Index
<http://pypi.python.org/pypi/LEPL>`_ for the use of setuptools.



Support
-------

I am using `Google Code <http://lepl.googlecode.com/>`_ for support
services.  Currently these are:

* A `mailing list / discussion group <http://groups.google.com/group/lepl>`_.

* An `issue tracker <http://code.google.com/p/lepl/issues>`_.

To ask questions, report bugs, and generally discuss LEPL, please post to the
`group <http://groups.google.com/group/lepl>`_.


Release History
---------------

==========  =======  ===========
Date        Version  Description
==========  =======  ===========
2009-01-29  1.0b1    Fighting with setuptools etc.
----------  -------  -----------
2009-01-29  1.0b2    Now with source, documentation and inline licence.
----------  -------  -----------
2009-01-30  1.0b3    Fixed version number confusion (was 0.1bx in some places).
----------  -------  -----------
2009-01-30  1.0rc1   With support.
==========  =======  ===========


.. index:: Python version
.. _versions:

Supported Versions
------------------

The code was written using Python 3.0.  It was then backported to Python 2.6
and appears to work fine there (except that the ``//`` operator doesn't
exist).

However, it's not regularly tested on anything other than 3.0.

It does not work with Python 2.5.  Incompatabilities include:

  * with contexts
  * setter decorators
  * {} formatting
  * ABC metaclasses
  * changed heapq API
  * except syntax


.. index:: licence, LGPL
.. _licence:

Licence
-------

LEPL is licensed under the `Lesser Gnu Public Licence
<http://www.gnu.org/licenses/lgpl.html>`_.  It is copyright 2009 Andrew Cooke
(andrew@acooke.org).

This documentation is licensed under the `Gnu Free Documentation Licence
<http://www.gnu.org/licenses/fdl.html>`_.  It is copyright 2009 Andrew Cooke
(andrew@acooke.org).

::
  
    LEPL is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
  
    LEPL is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.
  
    You should have received a copy of the GNU Lesser General Public License
    along with LEPL.  If not, see <http://www.gnu.org/licenses/>.
