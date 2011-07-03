#LICENCE


from lepl.rxpy.graph.support import node_iterator, ReadsGroup, contains_instance
from lepl.rxpy.support import RxpyError
from lepl.rxpy.graph.opcode import GroupReference, Conditional, StartGroup, Lookahead


def resolve_group_names(state):
    '''
    Calls "resolve" on group references and conditionals (sets index for
    a given name).

    Returns a list of actions that can be passed to the post-processor.
    '''
    resolve = lambda node: node.resolve(state)
    return [(GroupReference, resolve), (Conditional, resolve)]


def set_lookahead_properties():
    '''
    Sets "reads" and "mutates" properties on lookahead nodes.
    '''
    def set(node):
        node.reads = contains_instance(node.next[1], ReadsGroup)
        node.mutates = contains_instance(node.next[1], StartGroup)
        node.size = lambda groups: node.next[1].length(groups)
    return (Lookahead, set)


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
