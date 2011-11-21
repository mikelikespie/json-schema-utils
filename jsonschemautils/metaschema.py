from collections import namedtuple

from jsonschemautils.util import js_primitive

import json
import weakref
import itertools

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

class Schema(object):
    __slots__ = ("minimum", "maxItems", "_schema", "exclusiveMinimum", "id",
                 "_ref", "exclusiveMaximum", "title", "pattern",
                 "patternProperties", "extends", "type", "description",
                 "format", "minLength", "enum", "disallow", "divisibleBy",
                 "dependencies", "maxLength", "uniqueItems", "properties",
                 "additionalItems", "default", "items", "required", "maximum",
                 "minItems", "additionalProperties")

    __defaults__ = dict(exclusiveMinimum=False,
                        exclusiveMaximum=False,
                        patternProperties={},
                        extends={},
                        minLength=0,
                        divisibleBy=1,
                        dependencies={},
                        uniqueItems=False,
                        properties={},
                        additionalItems={},
                        required=False,
                        minItems=0,
                        additionalProperties={},
                        items=set(),
                        type=set())
    def __init__(self, raw_json=Undefined, **kwargs):

        self.properties = {}
        self.items = set()
        self.type = set()

        if raw_json is not Undefined:
            self.type = set([js_primitive(raw_json)])
            if isinstance(raw_json, dict):
                self.properties = dict((k,Schema(raw_json=v)) for k,v in raw_json.iteritems())
            elif isinstance(raw_json, list):
                self.items = set(Schema(raw_json=v) for v in raw_json)

        for k,v in kwargs.iteritems():
            getattr(self, k) # hack to validate we have this property
            setattr(self, k, v)

    def __schema_repr__(self):
        return dict((prop_name.replace("$", "_"), schema_repr(getattr(self, prop_name)))
                    for prop_name
                    in self.__slots__
                    if hasattr(self, prop_name) and \
                        schema_repr(getattr(self, prop_name)) != schema_repr(self.__defaults__.get(prop_name)))

    def __repr__(self):
        return '<Schema (%s)>' % json.dumps(schema_repr(self))


    def merge_copy(self, other):
        new_type = self.type | other.type

        new_items = self.items | other.items

        new_properties = {}

        all_property_names = set(self.properties.keys() + other.properties.keys())

        for prop_name in all_property_names:
            p = self.properties.get(prop_name)
            other_p = other.properties.get(prop_name)

            if p and other_p:
                new_properties[prop_name] = p.merge_copy(other_p)
            elif p:
                new_properties[prop_name] = p
            else:
                new_properties[prop_name] = other_p


        return Schema(items=new_items,
                      type=new_type,
                      properties=new_properties)


    def iterschemas(self, iter_items=True, iter_properties=True, current_path=()):
        iterchain = []

        ary_path = current_path + ('[]',)

        yield self, current_path
        
        if isinstance(self.items, Schema):
            for s, pth in self.items.iterschemas(iter_items, iter_properties, current_path=ary_path):
                yield s, pth

        elif isinstance(self.items, (set, list)):
            for i in self.items:
                if isinstance(i, Schema):
                    for s, pth in i.iterschemas(iter_items, iter_properties, current_path=ary_path):
                        yield s, pth

        for n, e in self.properties.iteritems():
            if isinstance(e, Schema):
                p_path = current_path + (n,)
                for s, pth in e.iterschemas(iter_items, iter_properties, current_path=p_path):
                    yield s, pth

    def all_schemas(self):
        return (s for s in itertools.chain(self.items, self.properties.itervalues())
                if isinstance(s, Schema))

    # Should this be immutable?
    def flatten_items(self):
        if self.items:
            def rfunc(cur_schema, schema):
                return cur_schema.merge_copy(schema)
            self.items = set([reduce(rfunc, self.items)])




