from collections import defaultdict
import abc
import weakref


def _list_or_single(iterable):
    """
    Returns a list if it has more than 1 elements.
    Otherwise, it will be the first item
    """
    l = list(iterable)
    if len(l) == 1:
        return l[0]
    else:
        return l

class Node(object):
    __metaclass__ = abc.ABCMeta

    id = None

    @property
    def children(self):
        """
        child nodes
        """
        return []
    
    @abc.abstractproperty 
    @property
    def schema(self):
        """
        returns a dictionary representation of this object
        """
        return dict(type=self._primitive_type)
    
    @property
    def _primitive_type(self):
        """
        object, string, etc
        """

    def make_ref(self, id):
        assert self.id is None or self.id == id 

        self.id = id
        return RefNode(self)

class TypeNode(Node):
    @property
    def schema(self):
        s = Node.schema
        s.update(self.items)
        return s

    __setattrs__ = ('type', 'example', 'id')

    def __init__(self):
        self.types = set()
        self.items = 
        self.possible_values = []
        self.properties = defaultdict(Node)
        self.name = None
        self.id = None
        self.extra_properties = dict()

    def add_type(self, typename):

    @property
    def children(self):
        return self.properties.values()

    @property
    def schema(self):
        property_vals = dict((name, p.schema)
                             for p
                             in self.properties.iteritems)

    @property
    def _primitive_type(self):
        return 'object'

class RefNode(Node):
    def __init__(self, ref):
        self.ref = ref

    @property
    def children(self):
        return self.ref.children

    @property
    def schema(self):
        return {'$ref':self.ref.id}

class Document(object):
    def __init__(self, rules=()):
        """
        :param rules: Rules to apply while walking
        :type rules: :class:`rules.BaseRule`
        """
 
        self.rules = rules

    def walk_document(self, document):
        if isinstance(document, list):
            for e in document:
                self._traverse(BuilderState((), e))
        else:
            self._traverse(BuilderState((), document))


    def _traverse(self, builder_state):
        path = builder_state.path
        element = builder_state.element

        # TODO: enum detection
        basetype = js_primitive(element)


        self._register_type(path, basetype, builder_state)

        if basetype == 'object':
            for k, v in element.iteritems():
                self._traverse(BuilderState(builder_state.path + (k,), v))

        elif basetype == 'array':
            array_path = path + ('$items',)
            for t in element:
                self._traverse(BuilderState(array_path, t))

    def _register_type(self, path, type, builder_state):
        nodes = [self.root_node]

        for el in path:
            n = nodes[-1]
            nodes.append(n.props[el])

        lastnode = nodes[-1]

        lastnode.possible_types.add(type)
        lastnode.possible_values.append(builder_state.element)

    @property
    def generated_schema(self):
        return self.root_node.schema
