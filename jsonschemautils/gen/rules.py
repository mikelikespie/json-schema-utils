"""
Rule based matching and transforming
"""

import re

SEP_TOKEN = '@@'

def BaseRule(object):
    """
    Abstract class for rules.
    """
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def apply(self, schema_node):
        """
        Applies a rule to the schema node

        :param schema_node: Node to apply to

        :return:
            - ``True`` to stop matching.
            - ``None`` or ``False`` to continue (by not returning anything you
                will continue)
        :rtype: bool or none
        """


def RuleSet(BaseRule):
    """
    Collection of rules that compose into a BaseRule
    """
    
    def __init__(self):
        self.rules = []


    def add_rule(self, rule):
        """Appends a rule to the :class:`RuleSet`"""
        self.rules.append(rule)


    def apply(self, schema_node):
        """Tries matching each subsequent rule until one says to stop"""
        for r in self.rules:
            if r.apply(schema_node):
                return True

        return None


def Rule(object):
    def __init__(self, matchers, mutation, stop_on_match=False):
        """
        :param matchers:
            A matcher function takes a single :class:`VisitorState`
            argument and returns ``True`` if it matches, others
        :type matchers:
            a single matcher function or :class:`tuple` or :class:`list`

        :param mutation:
            An instance of :class:`Mutation` which describes
            the transformation
        :type mutation: instance of :class:`Mutation`

        :param stop_on_match:
            Whether or not matching should stop after a match.
        :type stop_on_match: :class:`bool`
        """
        if isinstance(matcher, (list, tuple)):
            self.matchers = list(matchers)
        else:
            self.matchers = [matchers]

        self.mutation = mutation

    def apply(self, schema_node):
        """
        Iterates through the matchers
        """


def Matcher(object):
    """
    Class that represents matching a JSON path.
    """
    def __init__(self, path_query=None):
        """
        :param path_query:
            Query of path to match.

            examples::

                'entities.$items'   # matches every array element of entities
                '*.id'              # matches all properties named id
                '*.*_url'           # matches all properties that end with '_url'
        """

        if path_query:
            self.path_matcher = re.escape(query.replace('.', SEP_TOKEN)).replace('\\*', r'.*')
        else:
            self.path_matcher = None

    
    @abc.abstractmethod
    def __call__(self, parse_state):
        """
        :param parse_state: current parse state
        :returns: ``True`` if we have a match
        """
        if self.path_matcher:
            path = parse_state.path
            path_escaped = self._path_to_string_rep(path)

            if self.path_matcher.match(path_escaped):
                return True

        return False

    def _path_to_string_rep(self, path):
        """
        Converts a JSON path into a separated string.
        This is so we can do a regex match against the query path.
        """
        return SEP_TOKEN.join(e)



