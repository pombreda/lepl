
from unittest import TestCase
from traceback import format_exception_only, format_exc, print_exc


class Example(TestCase):
    
    def examples(self, examples):
        for (example, target) in examples:
            try:
                result = str(example())
            except Exception as e:
                print_exc()
                result = ''.join(format_exception_only(type(e), e))
            assert target == result, '"' + result + '"'
