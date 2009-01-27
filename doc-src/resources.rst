
Resource Management
===================


Streams
-------

LEPL can process simple strings and lists, but it can also use its own Stream
class as a wrapper for the input.  There are two advantages to doing this:

#. When reading from a file, the stream will not keep more data in memory than
   is necessary, so files larger than the available memory can be processed.

#. The stream provides access to the central Core instance, which supportsis
   necessary for both :ref:`debugging` and :ref:`depthcontrol`.

Streams are most simply created by using the ``parse...`` and ``match...``
methods that all matchers implement via `BaseMatcher
<../api/redirect.html#lepl.stream.StreamMixin>`_.


.. _depthcontrol:

Depth Control
-------------

.. warning::

  The functionality to limit the number of generators described in this
  section is not well understood.  The implementation is more complex than I
  would like and during development some unit tests changed results in a way
  that I cannot explain.

  By default these features are disabled --- the depth of searches is
  unrestricted.


