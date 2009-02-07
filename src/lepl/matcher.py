
from lepl.graph import ArgAsAttributeMixin, GraphWalkerMixin, ConstructorStr


class GraphNodeMixin(ArgAsAttributeMixin, GraphWalkerMixin):
    '''
    Allow the construction of a graph of matchers.
    '''

    def __init__(self):
        super(GraphNodeMixin, self).__init__()
        
    def __repr__(self):
        visitor = ConstructorStr()
        lines = self.walk(visitor)
        return visitor.postprocess(lines)
        