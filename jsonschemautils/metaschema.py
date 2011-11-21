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
                        id=None,
                        additionalProperties={},
                        items=set(),
                        type=set())

    def __init__(self, raw_json=Undefined, **kwargs):

        self.properties = {}
        self.items = set()
        self.type = set()
        self.id = None
        self._ref = None

        if raw_json is not Undefined:
            self.type = set([js_primitive(raw_json)])
            if isinstance(raw_json, dict):
                self.properties = dict((k,Schema(raw_json=v)) for k,v in raw_json.iteritems())
            elif isinstance(raw_json, list):
                self.items = set(Schema(raw_json=v) for v in raw_json)

        for k,v in kwargs.iteritems():
            setattr(self, k, v)

    def __schema_repr__(self):
        if self._ref:
            return {'$ref':self._ref.id}
        else:
            return dict((prop_name.replace("$", "_"), schema_repr(getattr(self, prop_name)))
                        for prop_name
                        in self.__slots__
                        if hasattr(self, prop_name) and \
                            schema_repr(getattr(self, prop_name)) != schema_repr(self.__defaults__.get(prop_name)))

    def __repr__(self):
        return '<Schema (%s)>' % json.dumps(schema_repr(self))


    def merge(self, other):
        self.type = self.type | other.type
        self.items = self.items | other.items

        for k,v in other.properties.iteritems():
            if k in self.properties:
                self.properties[k].merge(v)
            else:
                self.properties[k] = v

        if not self.id:
            self.id = other.id
        else:
            assert self.id == other.id or not other.id
            


    def iterschemas(self, current_path=('#',)):

        if self._ref:
            for e in self._ref.iterschemas(current_path):
                yield e
            return

        ary_path = current_path + ('[]',)

        yield self, current_path
        
        if isinstance(self.items, Schema):
            for s, pth in self.items.iterschemas(current_path=ary_path):
                yield s, pth

        elif isinstance(self.items, (set, list)):
            for i in self.items:
                if isinstance(i, Schema):
                    for s, pth in i.iterschemas(current_path=ary_path):
                        yield s, pth

        for n, e in self.properties.iteritems():
            if isinstance(e, Schema):
                p_path = current_path + (n,)
                for s, pth in e.iterschemas(current_path=p_path):
                    yield s, pth

    def to_ref(self, other_node):
        other_node.merge(self)
        self._ref = other_node

    # Should this be immutable?
    def flatten_items(self):
        if self.items:
            i = self.items.pop()
            for o in self.items:
                i.merge(o)
            self.items = set([i])
