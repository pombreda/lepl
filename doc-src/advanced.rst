
Advanced Use
============


.. index:: Configuration(), configuration, flatten(), compose_transforms(), auto_memoize(), default configuration
.. _configuration:

Configuration
-------------

The configuration is used when generating a parser from the matchers graph.
It is specified using `Configuration()
<api/redirect.html#lepl.config.Configuration>`_ which takes two arguments,
``rewriters`` and ``monitors``.

Most examples here use the default configuration, which is supplied by
`Configuration.default()
<api/redirect.html#lepl.config.Configuration.default>`_ .  This is currently
defined as::

  Configuration(
    rewriters=[flatten, compose_transforms, lexer_rewriter(), auto_memoize()],
    monitors=[lambda: TraceResults(False)])

The rewriters are described below (:ref:`rewriting`).

The monitor (which is passed to `trampoline()
<api/redirect.html#lepl.parser.trampoline>`_) enables the `Trace()
<api/redirect.html#lepl.functions.Trace>`_.


.. index:: rewriting
.. _rewriting:

Rewriting
---------

A grammar is specified by :ref:`matchers`, giving a collection of Python
objects.  More exactly, a directed graph of objects is created.  LEPL 2 was
designed so that this graph can be examined and modified before it is used as
a parser.

.. note::

  This is very powerful --- it allows LEPL to use some of the techniques that
  make "compiled" parsers more efficient --- but it can also introduce quite
  subtle errors.  The addition of user--defined rewriters is not encouraged
  unless you are *very* familiar with LEPL.

.. note::

  LEPL presents all matchers via a uniform interface, but in practice there
  are two distinct types: core classes and functions.  Only the core class
  instances are present in the graph described above.  The functions are
  evaluated during the definition of the grammar and return (usually after
  evaluating a whole chain of related functions) core class instances.

  So the functions can be considered "syntactic sugar", while the core classes
  are the "real matchers".  From the user's point of view, however, this
  distinction is somewhat arbitrary, which is why the functions have
  capitalised names and look like class constructors.

The work of modifying the matcher graph is done by functions called
*rewriters*.  They are specified in the :ref:`configuration`.  The following
rewriters are available:


.. index:: flatten()

Flatten And, Or

  The `flatten <api/redirect.html#lepl.rewriters.flatten>`_ rewriter
  combines nested `And() <api/redirect.html#lepl.functions.And>`_ and `Or()
  <api/redirect.html#lepl.functions.Or>`_ functions.  This helps improve
  efficiency.

  Nested matchers typically occur because each ``&`` and ``|`` operator
  generates a new matcher, so a sequence of matchers separated by ``&``, for
  example, generates several `And() <api/redirect.html#lepl.functions.And>`_
  functions.  This rewriter moves them into a single matcher, as might be
  expected from reading the grammar.  This should not change the "meaning" of
  the grammar or the results returned.

  This matcher is used in the default :ref:`configuration`.


.. index:: compose_transforms()

Composing and Merging Transforms

  The `Transform() <api/redirect.html#lepl.functions.Transform>`_ matcher is
  the "workhorse" that underlies `Apply()
  <api/redirect.html#lepl.functions.Apply>`_, ``>``, etc.  It changes the
  results returned by other functions.

  Because transforms are not involved in the work of matching --- they just
  modify the final results --- the effects of adjacent instances can be
  combined into a single operation.  In some cases they can also be merged
  into the operation of another matcher.  This is done by the
  `compose_transforms <api/redirect.html#lepl.rewriters.compose_transforms>`_
  rewriter.

  These operations should not change the "meaning" of the grammar or the
  results returned, but should improve performance by reducing the amount of
  :ref:`trampolining` made by the parser.

  This matcher is used in the default :ref:`configuration`.


.. index:: memoize()

Global Memoizer

  The `memoize() <api/redirect.html#lepl.rewriters.memoize>`_ rewriter applies
  a single memoizer to all functions.  For more information see
  :ref:`memoisation` below.


.. index:: optimize_or()
.. _optimizeor:

Optimize Or For Left Recursion

  When a left--recursive rule occurs in an `Or()
  <api/redirect.html#lepl.functions.Or>`_ matcher it is usually most efficient
  to make it the right--most alternative.  This allows other rules to consume
  input before the recursive rule is (re-)called.

  The `optimize_or(conservative)
  <api/redirect.html#lepl.rewriters.optimize_or>`_ rewriter tries to detect
  left--recursive rules and re-arranges `Or()
  <api/redirect.html#lepl.functions.Or>`_ matcher contents appropriately.

  The ``conservative`` parameter supplied to this rewriter (and a few more
  below) indicates how left--recursive rules are detected.  If true, all
  recursive paths are assumed to be left recursive.  If false then only those
  matchers that are in the left--most position of multiple arguments are used
  (except for `Or() <api/redirect.html#lepl.functions.Or>`_).

  This matcher is used in the default :ref:`configuration` via the
  `auto_memoize(conservative)
  <api/redirect.html#lepl.rewriters.auto_memoize>`_ rewriter (below).


.. index:: context_memoize()

Context--Sensitive Memoisation

  The `context_memoize(conservative)
  <api/redirect.html#lepl.rewriters.context_memoize>`_ rewriter applies a
  memoizer to all functions.  Whether `LMemo()
  <api/redirect.html#lepl.memo.LMemo>`_ or the `RMemo()
  <api/redirect.html#lepl.memo.RMemo>`_ depends on whether the matcher is part
  of a left--recursive rule.

  The memoizers are described in more detail in :ref:`memoisation` below.  The
  detection of left--recursive rules is explained in the :ref:`Optimize Or
  <optimizeor>` entry above.

  This matcher is used in the default :ref:`configuration` via the
  `auto_memoize(conservative)
  <api/redirect.html#lepl.rewriters.auto_memoize>`_ rewriter (below).


.. index:: auto_memoize()

Automatic Memoisation

  This calls the `optimize_or(conservative)
  <api/redirect.html#lepl.rewriters.optimize_or>`_ and
  `context_memoize(conservative)
  <api/redirect.html#lepl.rewriters.context_memoize>`_ rewriters, described
  above.  In the default :ref:`configuration`, when the ``conservative``
  parameter is omitted, `optimize_or(conservative=False)
  <api/redirect.html#lepl.rewriters.optimize_or>`_ and
  `context_memoize(conservative=True)
  <api/redirect.html#lepl.rewriters.context_memoize>`_ are used.


.. index:: regexp_rewriter()

Rewriting as Regular Expressions

  The `regexp_rewriter()
  <api/redirect.html#lepl.regexp.rewriters.regexp_rewriter>`_ attempts to
  replace matchers with a regular expression.  This gives a significant
  increase in efficiency if the parser matches complex strings (for example,
  `Float() <api/redirect.html#lepl.functions.Float>`_).

  It is not used by default 
  because it requires the data being matched to be a particular type, but
  for Unicode text it can be selected with `Configuration.nfa()
  <api/redirect.html#lepl.config.Configuration.nfa>`_ or `Configuration.dfa()
  <api/redirect.html#lepl.config.Configuration.dfa>`_ (the latter only gives a
  single, greedy match and so may change the results for ambiguous grammars).

  It makes little sense to replace efficient, simple matchers like `Literal()
  <api/redirect.html#lepl.matchers.Literal>`_ with regular expressions so the
  function `regexp_rewriter()
  <api/redirect.html#lepl.regexp.rewriters.regexp_rewriter>`_ takes a ``use``
  parameter.  When this parameter is ``False`` regular expressions are only
  used if they are part of a matcher tree that includes repetition.  This is
  the case for the provided configurations above, so they can be used without
  worrying that they may slow down parsers.

  There are various restrictions about which matchers can be translated to
  regular expressions.  The most important are that regular expressions cannot
  include recursive loops or transformations.  So rewriting of regular
  expressions is typically restricted to those parts of the parser that
  recognise individual words.
  

.. index:: lexer_rewriter()

Identifying Tokens and Building a Lexer

  `lexer_rewriter() <api/redirect.html#lepl.lexer.rewriters.lexer_rewriter>`_
  checks whether `Token() <api/redirect.html#lepl.lexer.matchers.Token>`_ matchers are used in the parser and, if so,
  constructs an appropriate :ref:`lexer`.

  This is included in the default :ref:`configuration`, but can be specified
  manually if the :ref:`lexer` settings need to be changed.


.. index:: search, backtracking
.. _backtracking:

Search and Backtracking
-----------------------

Since LEPL supports full backtracking via generators it is possible to request
all the alternative parses for a given input::

  >>> from lepl import *

  >>> any = Any()[:,...]
  >>> split = any & any & Eos()
  >>> match = split.match_string()

  >>> [pair[0] for pair in match('****')]
  [['****'], ['***', '*'], ['**', '**'], ['*', '***'], ['****']]

This shows that successive parses match less of the input with the first
option, indicating that the matching is *greedy*.

*Non-greedy* (generous?) matching is achieved by specifying an array slice
increment of ``'b'`` (or `BREADTH_FIRST
<api/redirect.html#lepl.functions.BREADTH_FIRST>`_)::

  >>> any = Any()[::'b',...]
  >>> split = any & any & Eos()
  >>> match = split.match_string()

  >>> [pair for (pair, stream) in match('****')]
  [['****'], ['*', '***'], ['**', '**'], ['***', '*'], ['****']]

The greedy and non--greedy repetitions are implemented by depth (default,
``'d'``, or `DEPTH_FIRST <api/redirect.html#lepl.functions.DEPTH_FIRST>`_),
and breadth--first searches (``'b'`` or `BREADTH_FIRST
<api/redirect.html#lepl.functions.BREADTH_FIRST>`_), respectively.

In addition, by specifying a slice increment of ``'g'`` (`GREEDY
<api/redirect.html#lepl.functions.GREEDY>`_), you can request a *guaranteed
greedy* match.  This evaluates all possibilities, before returning them in
reverse length order.  Typically this will be identical to depth--first
search, but it is possible for backtracking to produce a longer match in
complex cases --- this final option, by evaluating all cases, re--orders the
results as necessary.

Specifying ``'n'`` (`NON_GREEDY
<api/redirect.html#lepl.functions.NON_GREEDY>`_) gets the reverse ordering.

The tree implicit in the descriptions "breadth--first" and "depth--first" is
not the AST, nor the tree of matchers, but a tree based on matchers and
streams.  In the case of a single, repeated, match this is easy to visualise:
at any particular node the child nodes are generated by applying the matcher
to the various streams returned by the current match (none if this is a final
node, one for a simple match, several if the matcher backtracks).

So far so good.  Unfortunately the process is more complicated for `And()
<api/redirect.html#lepl.functions.And>`_ and `Or()
<api/redirect.html#lepl.functions.Or>`_.

In the case of `And() <api/redirect.html#lepl.functions.And>`_, the first
matcher is matched first.  The child nodes correspond to the various (with
backtracking) results of this match.  At each child node, the second matcher
is applied, generating new children.  This repeats until the scope of the
`And() <api/redirect.html#lepl.functions.And>`_ terminates at a depth in the
tree corresponding to the children of the last matcher.  Since `And()
<api/redirect.html#lepl.functions.And>`_ fails unless all matchers match, only
the final child nodes are possible results.  As a consequence, both breadth
and depth first searches would return the same ordering.  The `And()
<api/redirect.html#lepl.functions.And>`_ match is therefore unambiguous and the
implementation has no way to specify the (essentially meaningless) choice
between the two searches.

In the case of `Or() <api/redirect.html#lepl.functions.Or>`_ we must select
both the matcher and the result from the results available for that matcher.
A natural approach is to assign the first generation of children to the choice
of matcher, and the second level to the choice of result for the (parent)
matcher.  Again, this results in no ambiguity between breadth and depth--first
results.

However, there is also an intuitively attractive argument that breadth--first
search would return the first results of the different matches, in series,
before considering backtracking.  At the moment I do not see a "natural" way
to form such a tree, and so this is not implemented.  Feedback is appreciated.


.. index:: memoisation, RMemo(), LMemo(), memoize(), ambiguous grammars, left-recursion, context_memoize(), auto_memoize()
.. _memoisation:

Memoisation
-----------

A memoizer stores a matcher's results.  If it is called again in the same
context (during backtracking, for example), the stored result can be returned
without repeating the work needed to generate it.  This improves the
efficiency of the parser.

LEPL 2 has two memoizers.  The simplest is `RMemo()
<api/redirect.html#lepl.memo.RMemo>`_ which is a simple cache based on the
stream supplied.

For left--recursive grammars, however, things are more complicated.  The same
matcher can be called with the same stream at different "levels" of recursion
(for full details see :ref:`memoisation_impl`).  In this case, `LMemo()
<api/redirect.html#lepl.memo.LMemo>`_ must be used.

Memoizers can be specified directly in the grammar or they can be added by
:ref:`rewriting` the matcher graph.  

When added directly to the grammar a memoizer only affects the given
matcher(s).  For example::

  >>> matcher = Any('a')[:] & Any('a')[:] & RMemo(Any('b')[4])
  >>> len(list(matcher.match('aaaabbbb')))
  5

Here the `RMemo() <api/redirect.html#lepl.memo.RMemo>`_ avoids re-matching of
the "bbbb", but has no effect on the matching of the "a"s.

.. _left_recursion:

The simplest way to apply a memoizer to all matchers is with the `memoize()
<api/redirect.html#lepl.rewriters.memoize>`_ rewriter::

  >>> class VerbPhrase(Node): pass
  >>> class DetPhrase(Node): pass
  >>> class SimpleTp(Node): pass
  >>> class TermPhrase(Node): pass
  >>> class Sentence(Node): pass

  >>> verb        = Literals('knows', 'respects', 'loves')         > 'verb'
  >>> join        = Literals('and', 'or')                          > 'join'
  >>> proper_noun = Literals('helen', 'john', 'pat')               > 'proper_noun'
  >>> determiner  = Literals('every', 'some')                      > 'determiner'
  >>> noun        = Literals('boy', 'girl', 'man', 'woman')        > 'noun'
        
  >>> verbphrase  = Delayed()
  >>> verbphrase += verb | (verbphrase // join // verbphrase)      > VerbPhrase
  >>> det_phrase  = determiner // noun                             > DetPhrase
  >>> simple_tp   = proper_noun | det_phrase                       > SimpleTp
  >>> termphrase  = Delayed()
  >>> termphrase += simple_tp | (termphrase // join // termphrase) > TermPhrase
  >>> sentence    = termphrase // verbphrase // termphrase & Eos() > Sentence
    
  >>> p = sentence.null_matcher(
  >>>         Configuration(rewriters=[memoize(LMemo)], 
  >>>                       monitors=[lambda: TraceResults(False)]))
  >>> len(list(p('every boy or some girl and helen and john or pat knows '
  >>>            'and respects or loves every boy or some girl and pat or '
  >>>            'john and helen')))
  392

This example is left--recursive and very ambiguous.  With `LMemo()
<api/redirect.html#lepl.memo.LMemo>`_ added to all matchers it can be parsed
with no problems.

It is also possible to use the `context_memoize()
<api/redirect.html#lepl.rewriters.context_memoize>`_ or `auto_memoize()
<api/redirect.html#lepl.rewriters.auto_memoize>`_ rewriters.  Both of these
attempt to detect left--recursive rules, so that the less efficient `LMemo()
<api/redirect.html#lepl.memo.LMemo>`_ is only used where necessary.

The default :ref:`configuration` uses `auto_memoize(conservative=False)
<api/redirect.html#lepl.rewriters.auto_memoize>`_, which should provide the
most efficient parser in most cases.  It is possible that some grammars will
need to use the more conservative algorithm to detect left--recursive loops,
via `auto_memoize(conservative=True)
<api/redirect.html#lepl.rewriters.auto_memoize>`_.

