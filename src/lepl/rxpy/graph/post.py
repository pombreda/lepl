#LICENCE


from lepl.rxpy.graph.support import node_iterator
from lepl.rxpy.support import RxpyError
from lepl.rxpy.graph.opcode import GroupReference, Conditional


def resolve_group_names(state):
    '''
    Returns a list of actions that can be passed to the post-processor.
    '''
    resolve = lambda node: node.resolve(state)
    return [(GroupReference, resolve), (Conditional, resolve)]


def post_process(graph, actions):
    map = {}
    for (type_, function) in actions:
        if type_ not in map:
            map[type_] = function
        else:
            raise RxpyError('Conflicting actions for ' + str(type_))
    for node in node_iterator(graph):
        map.get(type(node), lambda x: None)(node)
    return graph
