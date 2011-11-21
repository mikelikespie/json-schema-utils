from collections import namedtuple

from jsonschemautils.util import js_primitive

import json
import weakref

class Undefined(object):
    @classmethod
    def __schema_repr__(cls):
        return "!!!!! UNDEFINED !!!!!"


def schema_repr(o):
    if hasattr(o, "__schema_repr__"):
        return o.__schema_repr__()
    elif isinstance(o, (list, tuple, set)):
        return list(schema_repr(e) for e in o)
    elif isinstance(o, dict):
        return dict((k,schema_repr(v)) for k,v in o.iteritems())
    else:
        return o


class TypeUnion(object):
    def __init__(self, types=(), default='any'):
        self.types = set(types)
        self.default = default

    
    def __schema_repr__(self):
        types = [schema_repr(t) for t in self.types]
        if len(types) == 1:
            single_obj = types[0]
            if isinstance(single_obj, dict):
                return types
            elif isinstance(single_obj, basestring):
                return single_obj
            else:
                raise Exception("unknown type %s", single_obj)
        elif types:
            return types
        else:
            return self.default

class Items(object):
    """
    Going to limit items to a single schema obj
    """
    def __init__(self):
        self.types = set()
        self.default = {}


    @property
    def schema_item(self):
        for t in self.types:
            if isinstance(t, Schema):
                return t

        return None

    def __schema_repr__(self):
        types = [schema_repr(t) for t in self.types]
        if len(types) == 1:
            single_obj = types[0]
            if isinstance(single_obj, dict):
                return types[0]
            elif isinstance(single_obj, basestring):
                return single_obj
            else: assert False
        elif types:
            return types
        else:
            return self.default



#def lazyproperty(real_name, default):
#    def get(self):
#        if hasattr(self, real_name):
#            return getattr(self, real_name)
#        else:
#            return default
#
#    def set(self, value):
#        setattr(self, real_name, value)
#
#
#    return property(get, set)



#class SchemaItems(object):
#    def __init__(self, Schema):

class Schema(object):
    __property_names__ = ("minimum", "maxItems", "_schema", "exclusiveMinimum", "id",
                          "_ref", "exclusiveMaximum", "title", "pattern",
                          "patternProperties", "extends", "type", "description",
                          "format", "minLength", "enum", "disallow", "divisibleBy",
                          "dependencies", "maxLength", "uniqueItems", "properties",
                          "additionalItems", "default", "items", "required", "maximum",
                          "minItems", "additionalProperties")
    minimum = Undefined
    maxItems = Undefined
    _schema = Undefined
    exclusiveMinimum = False
    id = Undefined
    _ref = Undefined
    exclusiveMaximum = False
    title = Undefined
    pattern = Undefined
    patternProperties = {}
    extends = {}
    description = Undefined
    format = Undefined
    minLength = 0
    enum = Undefined
    disallow = Undefined
    divisibleBy = 1
    dependencies = {}
    maxLength = Undefined
    uniqueItems = False
    properties = {}
    additionalItems = {}
    default = Undefined
    required = False
    maximum = Undefined
    minItems = 0
    additionalProperties = {}
    items = {}
    type = {}

    def __init__(self, **kwargs):
        self.opts_list_set = set()

        self.type = TypeUnion()
        self.items = Items()

        self.properties = {}

        self.patternProperties = {}
        self.extends = {}
        self.dependencies = {}
        self.additionalItems = {}
        self.additionalProperties = {}

        for k,v in kwargs.iteritems():
            getattr(self, k) # hack to validate we have this property
            setattr(self, k, v)

    def __schema_repr__(self):
        return dict((prop_name.replace("$", "_"), schema_repr(getattr(self, prop_name)))
                    for prop_name
                    in self.__property_names__
                    if schema_repr(getattr(self, prop_name)) != schema_repr(getattr(self.__class__, prop_name))) 

    def __repr__(self):
        return '<Schema (%s)>' % json.dumps(schema_repr(self))

    def add_type(self, typename):
        self.type.types.add(typename)

    def add_property(self, property_name):
        assert 'object' in self.type.types
        if property_name not in self.properties:
            self.properties[property_name] = Schema()

    def add_array_items_type(self, typename):
        assert 'array' in self.type.types
        self.items.types.add(typename)

    def add_array_items_schema(self):
        assert 'array' in self.type.types
        if self.items.schema_item is None:
            self.items.types.add(Schema())

    @property
    def items_schema(self):
        self.add_array_items_schema()
        return self.items.schema_item

    @property
    def property_schema(self, property_name):
        self.add_property(property_name)
        return self.properties[property_name]

    ## Merging
    def merge_example(self, element):
        self.merge_example_primitive(element)

        if isinstance(element, dict):
            self.merge_example_object(element)
        elif isinstance(element, list):
            self.merge_example_array(element)

    def merge_example_array(self, element):
        """
        right now we treat arrays as if they only can contain more objects
        """
        schema = self.items_schema
        for item in element:
            schema.merge_example(item)

    def merge_example_primitive(self, element):
        self.add_type(js_primitive(element))

    def merge_example_object(self, element):
        for name, prop in element.iteritems():
            self.add_property(name)
            schema = self.properties[name]
            schema.merge_example(prop)

