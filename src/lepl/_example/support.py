
from unittest import TestCase
from traceback import format_exception_only, format_exc


class Example(TestCase):
    
    def examples(self, examples):
        for (example, target) in examples:
            try:
                result = str(example())
            except Exception as e:
                result = ''.join(format_exception_only(type(e), e))
            assert target == result, '"' + result + '"'
