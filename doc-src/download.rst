
.. _download:

Download And Installation
=========================

.. warning::

  This is the very first release.  So there may be a bug or two.
  Please let me know at andrew@acooke.org.


Python 3.0
----------

As far as I can tell, setuptools (easyinstall) does not support Python 3.0
yet, so please use the source distribution below.


Python 2.6
----------

If you have `setuptools <http://pypi.python.org/pypi/setuptools>`_ installed
you should be able to install LEPL with Python 2.6 using::

  easyinstall lepl


Source and Documentation
------------------------

* `Source tarball <http://ww.acooke.org/lepl/src.tgz>`_

* `Source zip <http://ww.acooke.org/lepl/src.zip>`_

* `Document tarball <http://ww.acooke.org/lepl/doc.tgz>`_

* `Document zip <http://ww.acooke.org/lepl/doc.zip>`_

If you unpack/uncompress the source you can then copy the ``lepl`` directory
into your Python site packages directory.  This should install LEPL.


Release History
---------------

==========  =======  ===========
Date        Version  Description
==========  =======  ===========
2009-01-29  1.0b1    Fighting with setuptools etc.
----------  -------  -----------
2009-01-29  1.0b2    Now with source, documentation and inline licence.
==========  =======  ===========


.. index:: Python version

Supported Versions
------------------

The code was written using Python 3.0.  It was then backported to Python 2.6
and appears to work fine there (except that the ``//`` operator doesn't
exist).  It might even work with Python 2.5 if you add appropriate ``from
__future__ import ...`` in various places (you could make the `Matcher
<api/redirect.html#lepl.match.Matcher>`_ ABC a simple class without really
harming anything).

However, it's not regularly tested on anything other than 3.0.


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
