from collections import namedtuple

from jsonschemautils.util import js_primitive
from jsonschemautils.metaschema import Schema, schema_repr



class Document(object):
    def __init__(self, rules=()):
        """
        :param rules: Rules to apply while walking
        :type rules: :class:`rules.BaseRule`
        """
 
        self.rules = rules

        self.root = Schema()

    def merge_example(self, element):
        self.merge_example_primitive(gelement)

        if isinstance(element, dict):
            self.merge_example_object(gelement)
        elif isinstance(element, list):
            self.merge_example_array(gelement)

    def merge_example_array(self, element):
        """
        right now we treat arrays as if they only can contain more objects
        """
        schema = self.items_schema
        for item in element:
            self.merge_example(schema, item)

    def merge_example_primitive(self, element):
        self.add_type(js_primitive(element))

    def merge_example_object(self, element):
        for name, prop in element.iteritems():
            self.add_property(name)
            schema = self.properties[name]
            self.merge_example(schema, prop)


    def _schema_for_path(self, path):
        target_node = self.root_node

        for el in path:
            if el != '$items':
                target_node = target_node.properties[el]
            else:
                target_node = target_node.items

            nodes.append(n.props[el])


    def __repr__(self):
        return repr(self.root)

    @property
    def generated_schema(self):
        return self.root_node.schema
