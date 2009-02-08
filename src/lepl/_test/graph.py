
from unittest import TestCase


from lepl.graph import ArgAsAttributeMixin, preorder, postorder


class Node(ArgAsAttributeMixin):
    '''
    Has an 'invisible' label (not registered as an attribute).
    '''
    
    def __init__(self, label, *children):
        super(Node, self).__init__()
        self.label = label
        self._args(children=children)
        
    def __str__(self):
        return str(self.label)
    

class OrderTest(TestCase):
    
    def graph(self):
        return Node(1,
                    Node(11,
                         Node(111),
                         Node(112)),
                    Node(12))
        
    def test_preorder(self):
        result = [node.label for node in preorder(self.graph())]
        assert result == [1, 11, 111, 112, 12], result
        
    def test_postorder(self):
        result = [node.label for node in postorder(self.graph())]
        assert result == [111, 112, 11, 12, 1], result
        
        
        
        