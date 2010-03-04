# Welcome to LEPL - a parser for Python 2.6+

# All these examples will assume that we have imported the main package
from lepl import *

# Let's start with a typical problem: we want to parse the input for
# a search engine.  A request might be:
#   spicy meatballs OR "el bulli restaurant"

# Here is how we define the parser:
word = ~Lookahead('OR') & Word()
phrase = String()
with DroppedSpace():
    text = (phrase | word)[1:] > list
    query = text[:, Drop('OR')]

# and here is how we can use it:
query.parse('spicy meatballs OR "el bulli restaurant"')

# If you want to pause this demo, so that you can scroll back and 
# have a think, just click on the screen (click again to restart).

# It's interesting to see what is happening in a little more detail:
with TrackVariables():
    word = ~Lookahead('OR') & Word()
    phrase = String()
    with DroppedSpace():
        text = (phrase | word)[1:] > list
        query = text[:, Drop('OR')]

query.config.auto_memoize(full=True)
query.parse('spicy meatballs OR "el bulli restaurant"')
# The display above shows how the different variables are bound as
# the input stream is consumed.  This can be very useful for debugging.

# Just before calling the parser above we configured full memoization.
# This means that each matcher records previous matchers and so avoids
# earlier work.  The (lack of a) trace on a second call reflects this:
query.parse('spicy meatballs OR "el bulli restaurant"')

# TODO - sub matcher memoization
 

# You probably noticed that some "surprising" syntax above, in the
# way that we specify repeated matches - using [1:] for "one or more".
# This may seem a little odd, but soon feels very natural.

# For example, this means "between 3 and 5" (inclusive):
Any()[3:5].parse('1234')
Any()[3:5].parse('123456')

# And often, once we've matched something several times, we want to
# join the results together - we can use [...] for that:
Any()[3:5, ...].parse('1234')

# And (even more!) we can also specify a separator...
Any()[3:5, ';'].parse('1;2;3;4')
# ...which we often discard:
Any()[3:5, Drop(';')].parse('1;2;3;4')

# While we're looking at LEPL's syntax, it's worth pointing out that
# & and | do what you would expect:
(Digit() | Letter())[:].parse('abc123')
(Digit() & Letter())[:].parse('1a')




# A LEPL parser is built from matchers - you can define them yourself.
# For example, let's define a matcher for Capital letters

from string import ascii_uppercase

@function_matcher
def Capital(support, stream):
    if stream[0] in ascii_uppercase:
        return ([stream[0]], stream[1:])
    
# As you can see, a matcher takes a stream and, if the start of the
# stream matches, returns that (in a list) and the rest of the stream.

# We can test it out 
# (note how @function_matcher has changed how we call the matcher):
parser1 = Capital()
parser1.parse('A')

# LEPL automatically adds support for repetition:
parser2 = Capital()[3]
parser2.parse('ABC')

# which can have upper and lower bounds:
parser3 = Capital()[1:5]
parser3.parse('ABCD')

# and can join together matched letters:
parser4 = Capital()[3, ...]
parser4.parse('ABC')

# If the parser fails to match, we get an error:
parser4.parse('ABCD')


# But often we don't need to define our own matchers, because LEPL
# already provides a wide range.

# For example, Any(...) will match any of its arguments:

from string import ascii_lowercase
parser5 = Any(ascii_lowercase)[4]
parser5.match('abcd')

# And we can combine matchers together:
parser6 = Capital() + Any(ascii_lowercase)[1:,...]
parser6.parse('Capitalized')

# We can easily build more complex parsers:
lowercase = Any(ascii_lowercase)[1:,...]
first = Capital() + Any(ascii_lowercase)[1:,...]
following = 