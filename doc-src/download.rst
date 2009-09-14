
.. _install:

Download And Installation
=========================

LEPL is only available for Python 3 and 2.6.  See :ref:`versions` for more
information.

.. warning::

  When a new version of LEPL is close to being released there may be both a
  stable and a beta version available.  The main documentation (at
  www.acooke.org) describes the latest (possibly beta) version, but source and
  documentation for either version can be :ref:`downloaded <download>`.

  For more details, please read the information below.


Installation
------------

There are several ways to install LEPL --- they are described below, simplest
first.  If you want a local copy of the manual you should also read the
:ref:`localdocs` section.


Install With Setuptools / easy_install (Python 2.6)

  This installs the latest **stable** version and currently only works for
  **Python 2.6**.

  If you have `setuptools <http://pypi.python.org/pypi/setuptools>`_ installed
  you should be able to install LEPL using::

    easy_install lepl

  That's it.  There is no need to download anything beforehand;
  ``easy_install`` will do all the work.


.. _manual_install:

Install With Distutils / setup.py (Python 3 and 2.6)

  :ref:`download` and unpack a source package then run::

    python setup.py install

  For example, on Gnu/Linux (in the instructions below, "LEPL-xxx" would be
  "LEPL-\ |release|\ " for the current release)::

    wget http://lepl.googlecode.com/files/LEPL-xxx.tar.gz
    tar xvfz LEPL-xxx.tar.gz
    cd LEPL-xxx
    python setup.py install


Manual Install (experts only)

  :ref:`download` and unpack a source package then add to your ``PYTHONPATH``
  or ``site-packages``.


.. _download:

Download
--------

You can download the source and documentation packages (for both stable and
beta releases) from the `Support Site
<http://code.google.com/p/lepl/downloads>`_.

**Stable** source packages are also available from the `Python Package Index
<http://pypi.python.org/pypi/LEPL/>`_.


.. index:: Python version
.. _versions:

Testing
-------

Once installed you can test LEPL by running the self-test::

  >>> from lepl._test import all
  >>> all()

.. warning::

  Some test failures are expected with certain Python versions.  The test
  described above will check the failures against the version used and,
  if all is as expected, display "Looks OK to me!".

  Also, with easy_install and Python 2.6, a syntax error is printed during
  install (from a Python 3 print statement in lepl._example.separators).  You
  can safely ignore this.

Supported Versions
------------------

The code is targetted at Python 3, but various small modifications are added
to keep most packages (currently everything except binary parsing) working
with Python 2.6.

It is regularly tested on 2.6 and 3.1.

It does not work with Python 2.5.  Incompatibilities include:

  * with contexts
  * setter decorators
  * {} formatting
  * ABC metaclasses
  * changed heapq API
  * except syntax

