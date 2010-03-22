
Advanced Use
============


Configuration
-------------

Configuration for Lepl 4 has been completely revised.  Instead of using a
separate configuration object, a ``.config`` attribute on the macther is used.
This means that you can explore the available options at the Python prompt
(and perhaps via some IDEs).

For example::

  >>> dir(matcher.config)
  [... 'add_monitor', 'add_rewriter', 'alphabet', 'auto_memoize', 'blocks', 
  'changed', 'clear', 'compile_to_dfa', 'compile_to_nfa', ...]
  >>> help(matcher.config.compile_to_dfa)
  Help on method compile_to_dfa in module lepl.core.config:
  compile_to_dfa(self, force=False, alphabet=None) method of lepl.core.config.ConfigBuilder instance
      Compile simple matchers to DFA regular expressions.  This improves
      efficiency but may change the parser semantics slightly (DFA regular
      expressions do not provide backtracking / alternative matches).

Also, note that configuration methods can be chained together, making
configuration code more compact::

  >>> matcher.config.clear().lexer()

Common, Packaged Actions
~~~~~~~~~~~~~~~~~~~~~~~~

`.config.default() <api/redirect.html#lepl.core.config.ConfigBuilder.default>`_

  This sets the default configuration.  It is not needed when first using a
  matcher, but can be useful to "reset" a matcher to the default state.

  The default configuration is now (since Lepl 4) close to optimal; for many
  parsers no additional configuration is necessary.

`.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_

  This empties the current configuration (for example, removing the default
  settings).  If this is *not* used then any alterations are *relative* to the
  default settings.

`.config.default_line_aware() <api/redirect.html#lepl.core.config.ConfigBuilder.default_line_aware>`_

  This sets the default configuration when using line aware (block indented;
  offside rule) parsing.  See :ref:`offside`.

Other Packaged Actions
~~~~~~~~~~~~~~~~~~~~~~

`.config.lexer() <api/redirect.html#lepl.core.config.ConfigBuilder.lexer>`_ `.config.no_lexer() <api/redirect.html#lepl.core.config.ConfigBuilder.no_lexer>`_

  Detect the use of `Token()` and modify the parser to use the
  lexer. Typically this is called indirectly via `.config.default() <api/redirect.html#lepl.core.config.ConfigBuilder.default>`_
  (above).

`.config.line_aware() <api/redirect.html#lepl.core.config.ConfigBuilder.line_aware>`_

  Enable line aware parsing.  Typically this is called indirectly by
  `.config.default_line_aware() <api/redirect.html#lepl.core.config.ConfigBuilder.default_line_aware>`_ (above).

`.config.blocks() <api/redirect.html#lepl.core.config.ConfigBuilder.blocks>`_

  Enable offisde rule parsing.  Typically this is called indirectly by setting
  ``block_policy`` or ``block_start`` on `.config.default_line_aware() <api/redirect.html#lepl.core.config.ConfigBuilder.default_line_aware>`_
  (above).

Debug Actions
~~~~~~~~~~~~~

`.config.full_first_match() <api/redirect.html#lepl.core.config.ConfigBuilder.full_first_match>`_ `.config.no_full_first_match() <api/redirect.html#lepl.core.config.ConfigBuilder.no_full_first_match>`_

  Enable or disable the automatic generation of an error if the first match
  fails.

`.config.trace() <api/redirect.html#lepl.core.config.ConfigBuilder.trace>`_

  Add a monitor to trace results.  See ``TraceResults()``.  Removed by
  `.config.remove_all_monitors() <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_ or `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.

`.config.manage() <api/redirect.html#lepl.core.config.ConfigBuilder.manage>`_

  Add a monitor to manage resources.  See ``GeneratorManager()``. Removed by
  `.config.remove_all_monitors() <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_ or `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.

`.config.record_deepest() <api/redirect.html#lepl.core.config.ConfigBuilder.record_deepest>`_

  Add a monitor to record deepest match.  See ``RecordDeepest()``. Removed by
  `.config.remove_all_monitors() <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_ or `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.
    
Optimisation Actions
~~~~~~~~~~~~~~~~~~~~

`.config.flatten() <api/redirect.html#lepl.core.config.ConfigBuilder.flatten>`_ `.config.no_flatten() <api/redirect.html#lepl.core.config.ConfigBuilder.no_flatten>`_

  Combined nested `And() <api/redirect.html#lepl.matchers.combine.And>`_ and `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ matchers.

`.config.compile_to_dfa() <api/redirect.html#lepl.core.config.ConfigBuilder.compile_to_dfa>`_ `.config.compile_to_nfa() <api/redirect.html#lepl.core.config.ConfigBuilder.compile_to_nfa>`_ `.config.no_compile_to_regexp() <api/redirect.html#lepl.core.config.ConfigBuilder.no_compile_to_regexp>`_

  Compile simple matches to regular expressions.

``config.optimize_or()`` `.config.no_optimize_or() <api/redirect.html#lepl.core.config.ConfigBuilder.no_optimize_or>`_

  Rearrange arguments to `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ so that left-recursive matchers are tested
  last.  This improves efficiency, but may alter the parser semantics (the
  ordering of multiple results with ambiguous grammars may change).

``.config.direct_eval() `.config.no_direct_eval() <api/redirect.html#lepl.core.config.ConfigBuilder.no_direct_eval>`_

  Combine simple matchers so that they are evaluated without trampolining.

`.config.compose_transforms() <api/redirect.html#lepl.core.config.ConfigBuilder.compose_transforms>`_ `.config.no_compose_transforms() <api/redirect.html#lepl.core.config.ConfigBuilder.no_compose_transforms>`_

  Combine transforms (functions applied to results) with matchers.
        
`.config.auto_memoize() <api/redirect.html#lepl.core.config.ConfigBuilder.auto_memoize>`_ `.config.left_memoize() <api/redirect.html#lepl.core.config.ConfigBuilder.left_memoize>`_ `.config.right_memoize() <api/redirect.html#lepl.core.config.ConfigBuilder.right_memoize>`_ `.config.no_memoize() <api/redirect.html#lepl.core.config.ConfigBuilder.no_memoize>`_

  Remember previous inputs and results for matchers so that work is not
  repeated.

Low Level Actions
~~~~~~~~~~~~~~~~~

These methods are used internally.  They may also be useful if you are
developing a completely new functionality that is not supported by the "higher
level" actions described above.

`.config.add_rewriter() <api/redirect.html#lepl.core.config.ConfigBuilder.add_rewriter>`_ `.config.remove_rewriter() <api/redirect.html#lepl.core.config.ConfigBuilder.remove_rewriter>`_ `.config.remove_all_rewriters() <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_rewriters>`_

  Add or remove a rewriter, or remove all rewriters (possibly of a given
  type).  Rewriters manipulate the matchers before the parser is used.  This
  allows Lepl to use some of the techniques that make "compiled" parsers more
  efficient --- but it can also introduce quite subtle errors.  The addition
  of user--defined rewriters is not encouraged unless you are *very* familiar
  with Lepl.

`.config.add_monitor() <api/redirect.html#lepl.core.config.ConfigBuilder.add_monitor>`_ ``config.remove_all_monitors()``

  Add a monitor, or remove all monitors.  Monitors implement a callback
  interface that receives information about how Lepl is working.  They can be
  used to share state across matchers, or to generate debugging information,
  for example.

`.config.stream_factory() <api/redirect.html#lepl.core.config.ConfigBuilder.stream_factory>`_

  Set the stream factory.  This changes the class used to generate the stream
  for the parser, given some input (for example, `matcher.parse_string() <api/redirect.html#lepl.core.config.ParserMixin.parse_string>`_
  will call the ``from_string()`` method on this factory, to convert the
  string into a suitable stream).

``config.alphabet()``

  Set the alphabet, used by rgegular expressions.  The default alphabet is
  suitable for Unicode data.

Argument Actions
~~~~~~~~~~~~~~~~

Sometimes the same argument must be set on many matchers.  Rather that setting
each matcher individually, it is possible to set them all, via the
configuration.  These are used internally, to implement packaged actions;
end-users should not need to call these methods in "normal" use.

`.config.set_arguments() <api/redirect.html#lepl.core.config.ConfigBuilder.set_arguments>`_ ``config.no_set_argmuents()``

  Set an argument, or clear all such settings.

`.config.set_alphabet_arg() <api/redirect.html#lepl.core.config.ConfigBuilder.set_alphabet_arg>`_

  Set the ``alphabet=...`` argument.  If no value is given then the value
  given earlier to `.config.argument() <api/redirect.html#lepl.core.config.ConfigBuilder.argument>`_ (or, if no value was given, the
  default Unicode alphabet) is used.

`.config.set_block_policy_arg() <api/redirect.html#lepl.core.config.ConfigBuilder.set_block_policy_arg>`_

  Set the block policy on all ``Block()`` instances.











.. index:: configuration, flatten(), compose_transforms(), auto_memoize(), default configuration
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

The monitors are combined and passed to `trampoline()
<api/redirect.html#lepl.parser.trampoline>`_.  `TraceResults() <api/redirect.html#lepl.trace.TraceResults>`_ enables the
`Trace() <api/redirect.html#lepl.matchers.monitor.Trace>`_ matcher.


.. index:: rewriting
.. _rewriting:

Rewriting
---------

A grammar is specified by :ref:`matchers`, giving a collection of Python
objects.  More exactly, a directed graph of objects is created.  Lepl 2 was
designed so that this graph can be examined and modified before it is used as
a parser.

.. note::

  Modifying the matcher graph is a very powerful tool --- it allows Lepl to
  use some of the techniques that make "compiled" parsers more efficient ---
  but it can also introduce quite subtle errors.  The addition of
  user--defined rewriters is not encouraged unless you are *very* familiar
  with Lepl.

.. note::

  Lepl presents all matchers via a uniform interface, but in practice there
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
  combines nested `And() <api/redirect.html#lepl.matchers.combine.And>`_ and `Or()
  <api/redirect.html#lepl.matchers.combine.Or>`_ functions.  This helps improve
  efficiency.

  Nested matchers typically occur because each ``&`` and ``|`` operator
  generates a new matcher, so a sequence of matchers separated by ``&``, for
  example, generates several `And() <api/redirect.html#lepl.matchers.combine.And>`_
  functions.  This rewriter moves them into a single matcher, as might be
  expected from reading the grammar.  This should not change the "meaning" of
  the grammar or the results returned.

  This matcher is used in the default :ref:`configuration`.


.. index:: compose_transforms()

Composing and Merging Transforms

  The `Transform() <api/redirect.html#lepl.functions.Transform>`_ matcher is
  the "workhorse" that underlies `Apply()
  <api/redirect.html#lepl.matchers.derived.Apply>`_, ``>``, etc.  It changes the
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
  <api/redirect.html#lepl.matchers.combine.Or>`_ matcher it is usually most efficient
  to make it the right--most alternative.  This allows other rules to consume
  input before the recursive rule is (re-)called.

  The `optimize_or(conservative)
  <api/redirect.html#lepl.rewriters.optimize_or>`_ rewriter tries to detect
  left--recursive rules and re-arranges `Or()
  <api/redirect.html#lepl.matchers.combine.Or>`_ matcher contents appropriately.

  The ``conservative`` parameter supplied to this rewriter (and a few more
  below) indicates how left--recursive rules are detected.  If true, all
  recursive paths are assumed to be left recursive.  If false then only those
  matchers that are in the left--most position of multiple arguments are used
  (except for `Or() <api/redirect.html#lepl.matchers.combine.Or>`_).

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
  `Float() <api/redirect.html#lepl.matchers.derived.Float>`_).

  It makes little sense to replace efficient, simple matchers like `Literal()
  <api/redirect.html#lepl.matchers.core.Literal>`_ with regular expressions so the
  function `regexp_rewriter()
  <api/redirect.html#lepl.regexp.rewriters.regexp_rewriter>`_ takes a ``use``
  parameter.  When this parameter is ``False`` regular expressions are only
  used if they are part of a matcher tree that includes repetition.  This
  (``False``) is the case for the configurations above.

  There are various restrictions about which matchers can be translated to
  regular expressions.  The most important are that regular expressions cannot
  include recursive loops or transformations.  So rewriting of regular
  expressions is typically restricted to those parts of the parser that
  recognise individual words.
  
  This rewriter is not used by default because tests showed that in many cases
  it was no faster than the normal approach, while it runs the risk of
  changing the meaning of the grammar, adds significant complexity to the
  system, and requires the data being matched to be a particular type.  But
  for Unicode text it can be selected with `Configuration.nfa()
  <api/redirect.html#lepl.config.Configuration.nfa>`_ or `Configuration.dfa()
  <api/redirect.html#lepl.config.Configuration.dfa>`_ (the latter only gives a
  single, greedy match and so may change the results for ambiguous grammars).


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

Since Lepl supports full backtracking via generators it is possible to request
all the alternative parses for a given input::

  >>> from lepl import *

  >>> any = Any()[:,...]
  >>> split = any & any & Eos()
  >>> match = split.match_string()

  >>> [pair[0] for pair in match('****')]
  [['****'], ['***', '*'], ['**', '**'], ['*', '***'], ['****']]

This shows that successive parses match less of the input with the first
matcher, indicating that the matching is *greedy*.

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
<api/redirect.html#lepl.matchers.combine.And>`_ and `Or()
<api/redirect.html#lepl.matchers.combine.Or>`_.

In the case of `And() <api/redirect.html#lepl.matchers.combine.And>`_, the first
matcher is matched first.  The child nodes correspond to the various (with
backtracking) results of this match.  At each child node, the second matcher
is applied, generating new children.  This repeats until the scope of the
`And() <api/redirect.html#lepl.matchers.combine.And>`_ terminates at a depth in the
tree corresponding to the children of the last matcher.  Since `And()
<api/redirect.html#lepl.matchers.combine.And>`_ fails unless all matchers match, only
the final child nodes are possible results.  As a consequence, both breadth
and depth first searches would return the same ordering.  The `And()
<api/redirect.html#lepl.matchers.combine.And>`_ match is therefore unambiguous and the
implementation has no way to specify the (essentially meaningless) choice
between the two searches.

In the case of `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ we must select
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

Lepl 2 has two memoizers.  The simplest is `RMemo()
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

