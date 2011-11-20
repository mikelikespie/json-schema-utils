from collections import namedtuple

from schema import Node
from jsonschemautils.util import js_primitive
from rules import RuleSet


_BuilderState = namedtuple('BuilderState', ['path', 'element'])
class BuilderState(_BuilderState):
    """
    State of the visitor
    """


class DocumentVisitor(object):
    def __init__(self, rules=RuleSet()):
        """
        :param rules: Rules to apply while walking
        :type rules: :class:`rules.BaseRule`
        """
 
        self.root_node = Node()
        self.root_node.possible_types.add('object')
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
