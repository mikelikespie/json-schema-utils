from collections import defaultdict

class Node(object):
    def __init__(self):
        self.possible_types = set()
        self.possible_values = []
        self.props = defaultdict(Node)
        self.name = None
        self.id = None
        self.extra_props = dict()

    def _schema_for_type(self, type):
        """This is ugly.  Needs some rewriting"""
        if type == 'object':
            return dict(
                type='object',
                properties=dict(
                    (k, p.schema)
                    for k, p 
                    in self.props.iteritems()))
        if type == 'array':
            return dict(
                type='array',
                items=self.props['$items'].schema
            )
        return dict(type=type)

    @property
    def schema(self):
        ret = {}
        if self.id:
            ret['id'] = self.id

        if not self.possible_types:
            return 'UNKNOWN TYPE'

        if len(self.possible_types) > 1:
            return dict(type=[self._schema_for_type(t)['type'] for t in self.possible_types])
        else:
            return self._schema_for_type(list(self.possible_types)[0])

