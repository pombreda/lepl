
from unittest import TestCase


from lepl.graph \
    import ArgAsAttributeMixin, preorder, postorder, reset, ConstructorWalker, \
           Clone, make_proxy, TreeIndex, BEFORE


class Node(ArgAsAttributeMixin):
    
    def __init__(self, label, *nodes):
        super(Node, self).__init__()
        self._arg(label=label)
        self._args(nodes=nodes)
        
    def __str__(self):
        return str(self.label)
    
    def __repr__(self):
        args = [str(self.label)]
        args.extend(map(repr, self.nodes))
        return 'Node(%s)' % ','.join(args)
    
    def __getitem__(self, index):
        return self.nodes[index]
    
    def __len__(self):
        return len(self.nodes)
    

def graph():
    return Node(1,
                Node(11,
                     Node(111),
                     Node(112)),
                Node(12))
        
        
class OrderTest(TestCase):
    
    def test_preorder(self):
        result = [node.label for node in preorder(graph())]
        assert result == [1, 11, 111, 112, 12], result
        
    def test_postorder(self):
        result = [node.label for node in postorder(graph())]
        assert result == [111, 112, 11, 12, 1], result
        
        
class ResetTest(TestCase):
    
    def test_reset(self):
        nodes = preorder(graph())
        assert next(nodes).label == 1
        assert next(nodes).label == 11
        reset(nodes)
        assert next(nodes).label == 1
        assert next(nodes).label == 11


class CloneTest(TestCase):
    
    def test_simple(self):
        g1 = graph()
        g2 = ConstructorWalker(g1)(Clone())
        assert repr(g1) == repr(g2)
        assert g1 is not g2
    
    def assert_same(self, text1, text2):
        assert self.__clean(text1) == self.__clean(text2), self.__clean(text1)
    
    def __clean(self, text):
        depth = 0
        result = ''
        for c in text:
            if c == '<':
                depth += 1
            elif c == '>':
                depth -= 1
            elif depth == 0:
                result += c
        return result

    def test_loop(self):
        (s, n) = make_proxy()
        g1 = Node(1,
                Node(11,
                     Node(111),
                     Node(112),
                     n),
                Node(12))
        s(g1)
        g2 = ConstructorWalker(g1)(Clone())
        self.assert_same(repr(g1), repr(g2))

    def test_loops(self):
        (s1, n1) = make_proxy()
        (s2, n2) = make_proxy()
        g1 = Node(1,
                Node(11,
                     Node(111, n2),
                     Node(112),
                     n1),
                Node(12, n1))
        s1(g1)
        s2(next(g1.children()))
        g2 = ConstructorWalker(g1)(Clone())
        self.assert_same(repr(g1), repr(g2))
        
    def test_loops_with_proxy(self):
        (s1, n1) = make_proxy()
        (s2, n2) = make_proxy()
        g1 = Node(1,
                Node(11,
                     Node(111, n2),
                     Node(112),
                     n1),
                Node(12, n1))
        s1(g1)
        s2(next(g1.children()))
        g2 = ConstructorWalker(g1)(Clone())
        g3 = ConstructorWalker(g2)(Clone())
        self.assert_same(repr(g1), repr(g3))
#        print(repr(g3))


class IndexTest(TestCase):
    
    def test_traversal(self):
        tree = Node('a', Node('b', 1, 2), 3, Node('c', Node('d'), 4, Node('e', 5, 6), 7))
        class Record(TreeIndex):
            def __init__(self):
                super(Record, self).__init__(tree, Node)
                self.all = ''
                self.preorder = ''
                self.postorder = ''
                self.children = ''
            def leaf(self, node):
                self.all += str(node)
                self.children += str(node)
            def before(self, node):
                self.preorder += node.label
                self.all += node.label
            def after(self, node):
                self.postorder += node.label
                self.all += node.label
        r = Record()
        r.run()
        assert r.all == 'ab12b3cdd4e56e7ca', r.all
        assert r.preorder == 'abcde', r.preorder
        assert r.postorder == 'bdeca', r.postorder
        assert r.children == '1234567', r.children

        