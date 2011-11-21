"""
Small hackish script that will generate you some semblance of a metaschema by pssing it the 
schema definition
"""

import argparse
import sys
import json

def print_schema(class_name, schema):
    print 'class %s(BaseNode):' % class_name
    print '    __property_names__ = (%s)' % ',\n                          '.join(
        '"%s"' % k.replace('$', '_') for k in schema.get('properties', {}).keys())

    for property_name, property in schema.get('properties', {}).iteritems():
        safe_property_name = property_name.replace('$', '_')
        default = property.get('default', 'Undefined')
        print '    %s = %s' % (safe_property_name, default)
        
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', type=argparse.FileType('r'), nargs='?', metavar='INPUT_JSON', default=sys.stdin)

    args = parser.parse_args()

    schema = json.load(args.input_file)

    print 'import json'
    print
    print 'class Undefined: pass\n'
    print
    print 'def schema_repr(o):'
    print '    if hasattr(o, "__schema_repr__"):'
    print '        return o.__schema_repr__()'
    print '    else:'
    print '        return o'
    print 
    print 'class BaseNode(object):'
    print '    def __init__(self, **kwargs):'
    print '         for k,v in kwargs.iteritems():'
    print '             getattr(self, k) # hack to validate we have this property'
    print '             setattr(self, k, v)'
    print
    print '    def __schema_repr__(self):'
    print '        return dict((prop_name.replace("$", "_"), schema_repr(getattr(self, prop_name)))'
    print '                    for prop_name'
    print '                    in self.__property_names__'
    print '                    if getattr(self, prop_name) != getattr(self.__class__, prop_name)) '
    print
    print '    def __repr__(self):'
    print '        return json.dumps(schema_repr(self))'


    print_schema('Schema', schema)
    print_schema('Type', schema['properties']['type'])
