
from unittest import TestCase
from traceback import format_exception_only


class Example(TestCase):
    
    def examples(self, examples):
        for (example, target) in examples:
            try:
                result = str(example())
            except Exception:
                result = '\n'.join(format_exception_only(None, None))
            assert target == result, result
            
