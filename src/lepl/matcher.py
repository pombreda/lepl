

class NodeMixin(object):
    '''
    Allow the construction of a graph of matchers.
    '''

    def __init__(self):
        super(NodeMixin, self).__init__()
        self.arg_names = []
        self.__walker = None
        
    def __arg(self, **kargs):
        assert len(kargs) == 1
        for name in kargs:
            value = kargs[name]
            setattr(self, name, kargs[name])
            return name
            
    def _arg(self, **kargs):
        '''
        Set named arg as attribute and save name for future reconstruction.
        '''
        self.arg_names.append(self.__arg(**kargs))
        
    def _args(self, **kargs):
        '''
        Set named *arg as attribute and save name for future reconstruction.
        '''
        self.arg_names.append('*' + self.__arg(**kargs))
        
    def walk(self, visitor):
        if self.__walker is None:
            self.__walker = Walker(self)
        return self.__walker(visitor)
        
    def __repr__(self):
        visitor = MatcherStr()
        lines = self.walk(visitor)
        return visitor.postprocess(lines)


class Visitor(object):
    
    def __init__(self):
        self.type_ = None
        self.loop = None
        
    def node(self, *args, **kargs):
        pass
    
    def arg(self, value):
        pass


class Walker(object):
    
    def __init__(self, root):
        self.__root = root
        
    def __call__(self, visitor):
        visited = set()
        results = {}
        stack = [self.__root]
        while stack:
            node = stack[-1]
            extended = False
            if node not in visited:
                for child in self.__children(node):
                    stack.append(child)
                    extended = True
            visited.add(node)
            if not extended:
                visitor.type_ = type(node)
                (args, kargs) = self.__arguments(node, visitor, results)
                results[node] = visitor.node(*args, **kargs)
                stack.pop(-1)
        return results[self.__root]

    def __children(self, node):
        for name in node.arg_names:
            if name.startswith('*'):
                for child in getattr(node, name[1:]):
                    if isinstance(child, NodeMixin):
                        yield child
            else:
                child = getattr(node, name)
                if isinstance(child, NodeMixin):
                    yield child
    
    def __arguments(self, node, visitor, results):
        args = []
        kargs = {}
        for name in node.arg_names:
            if name.startswith('*'):
                for child in getattr(node, name[1:]):
                    args.append(self.__value(child, visitor, results))
            else:
                kargs[name] = self.__value(getattr(node, name), visitor, results)
        return (args, kargs)
    
    def __value(self, node, visitor, results):
        if isinstance(node, NodeMixin):
            if node in results:
                return results[node]
            else:
                return visitor.loop
        else:
            return visitor.arg(node)
        
                
class MatcherStr(Visitor):
    
    def __init__(self):
        super(MatcherStr, self).__init__()
        self.loop = [[0, '<loop>']]
    
    def node(self, *args, **kargs):
        contents = []
        for arg in args:
            if contents: contents[-1][1] += ', '
            contents.extend([indent+1, line] for (indent, line) in arg)
        for name in kargs:
            if contents: contents[-1][1] += ', '
            arg = kargs[name]
            contents.append([arg[0][0]+1, name + '=' + arg[0][1]])
            contents.extend([indent+1, line] for (indent, line) in arg[1:])
        lines = [[0, self.type_.__name__ + '(']] + contents
        lines[-1][1] += ')'
        return lines
    
    def arg(self, value):
        return [[0, repr(value)]]

    def postprocess(self, lines):
        '''
        Ugly, bug-prone and completely ad-hoc, but it seems to work....
        '''
        sections = []
        (scan, indent) = (0, -1)
        while scan < len(lines):
            (i, _) = lines[scan]
            if i > indent:
                indent = i
                sections.append((indent, scan))
            elif i < indent:
                (scan, indent) = self.__compress(lines, sections.pop(-1)[1], scan)
            scan = scan + 1
        while sections:
            self.__compress(lines, sections.pop(-1)[1], len(lines))
        return self.__format(lines)
    
    def __compress(self, lines, start, stop):
        try:
            return self.__all_on_one_line(lines, start, stop)
        except:
            return self.__bunch_up(lines, start, stop)
        
    def __bunch_up(self, lines, start, stop):
        (indent, _) = lines[start]
        while start+1 < stop:
            if indent == lines[start][0] and \
                    (start+1 >= stop or indent == lines[start+1][0]) and \
                    (start+2 >= stop or indent == lines[start+2][0]) and \
                    indent + len(lines[start][1]) + len(lines[start+1][1]) < 80:
                lines[start][1] += lines[start+1][1]
                del lines[start+1]
                stop -= 1
            else:
                start += 1
        return (stop, indent-1)

    def __all_on_one_line(self, lines, start, stop):
        (indent, text) = lines[start-1]
        size = indent + len(text) 
        for (_, extra) in lines[start:stop]:
            size += len(extra)
            if size > 80:
                raise Exception('too long')
            text += extra
        lines[start-1] = [indent, text]
        del lines[start:stop]
        return (start-1, indent)

    def __format(self, lines):
        return '\n'.join(' ' * indent + line for (indent, line) in lines)
                
        