import yaml

def setup_yaml():
    """
    Sets up yaml to write out unicode as standard strings, and interpret
    strings as unicode
    """

    def represent_unicode(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    def construct_unicode(loader, node):
        return unicode(loader.construct_scalar(node))

    yaml.add_representer(unicode, represent_unicode)
    yaml.add_constructor("tag:yaml.org,2002:str", construct_unicode)


js_primitive_mappings = [
    (dict,       'object'),
    (basestring, 'string'),
    (list,       'array'),
    (bool,       'boolean'),
    (int,        'integer'),
    (float,      'float'),
    (type(None), 'null'),
]

def js_primitive(python_obj):
    for type, primitive in js_primitive_mappings:
        if isinstance(python_obj, type):
            return primitive

    raise Exception("Could not match primitive for python object %s" % python_obj)
