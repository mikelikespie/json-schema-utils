from collections import namedtuple

from schema import Node
from jsonschemautils.util import js_primitive

_VisitorState = namedtuple('VisitorState', ['path', 'contents'])
class VisitorState(_VisitorState):
    """
    State of the visitor
    """


class DocumentVisitor(object):
    def __init__(self):
        self.root_node = Node()
        self.root_node.possible_types.add(('type', 'object'))

    def walk_document(self, document):
        if isinstance(document, list):
            for e in document:
                self._traverse(e, ())
        else:
            self._traverse(document, ())


    def _traverse(self, element, path):
        # TODO: enum detection
        basetype = js_primitive(element)

        override = None #override_type(element, path)

        self.register_type(path, ('type', basetype), element, override)

        if override:
            path = (override,)

        if basetype == 'object':
            for k, v in element.iteritems():
                self._traverse(v, (path + (k,)))

        elif basetype == 'array':
            array_path = path + ('$items',)
            for t in element:
                self._traverse(t, array_path)

    def register_type(self, path, type, content, override, set_id=None):
        if override:
            register_type((override,), type, content, None, override)
            type = ('$ref', override)

        nodes = [self.root_node]

        for el in path:
            n = nodes[-1]
            nodes.append(n.props[el])

        lastnode = nodes[-1]

        lastnode.possible_types.add(type)
        lastnode.possible_values.append(content)

        if set_id:
            print "Setting Id"
            lastnode.id = set_id


    @property
    def generated_schema(self):
        return self.root_node.schema
