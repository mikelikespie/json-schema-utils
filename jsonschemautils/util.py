import yaml



_SORT_ORDERS=[
    'description',
    'id',
    'type',
    'items',
    'properties']


def _sort_func((a, _),(b, __)):
    if a in _SORT_ORDERS and b in _SORT_ORDERS:
        return cmp(_SORT_ORDERS.index(a), _SORT_ORDERS.index(b))
    if a in _SORT_ORDERS:
        return -1
    if b in _SORT_ORDERS:
        return 1
    return cmp(a,b)

def setup_yaml():
    """
    Sets up yaml to write out unicode as standard strings, and interpret
    strings as unicode
    """

    def represent_unicode(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    def represent_dict(dumper, data):
        d = data.items()
        d.sort(_sort_func)
        return dumper.represent_mapping("tag:yaml.org,2002:map", d)

    def construct_unicode(loader, node):
        return unicode(loader.construct_scalar(node))

    yaml.add_representer(unicode, represent_unicode)
    yaml.add_representer(dict, represent_dict)
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
