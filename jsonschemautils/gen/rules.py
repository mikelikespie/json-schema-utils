"""
Rule based matching and transforming
"""

import re
import itertools
import abc

SEP_TOKEN = '@@'

class BaseRule(object):
    """
    Abstract class for rules.
    """
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def match(self, visitor_state):
        """
        Applies a rule to the schema node

        :param schema_node: Node to match to

        :return:
            - ``True`` to stop matching.
            - ``None`` or ``False`` to continue (by not returning anything you
                will continue)
        :rtype: bool or none
        """


class RuleSet(BaseRule):
    """
    Collection of rules that compose into a BaseRule
    """
    def __init__(self, rules = []):
        self.rules = rules

    def add_rule(self, rule):
        """Appends a rule to the :class:`RuleSet`"""
        self.rules.append(rule)


    def match(self, visitor_state):
        """Tries matching each subsequent rule until one says to stop"""
        return itertools.join.from_iterable(
            r.match(visitor_state) for r in self.rules)


class Rule(BaseRule):
    def __init__(self, matchers, transformations):
        """
        :param matchers:
            A matcher function takes a single :class:`VisitorState`
            argument and returns ``True`` if it matches, others
        :type matchers:
            a single matcher function or :class:`tuple` or :class:`list`

        :param transformations:
            An instance of :class:`Transformation` which describes
            the transformation
        :type transformations: instance of :class:`Transformation`

        :param stop_on_match:
            Whether or not matching should stop after a match.
        :type stop_on_match: :class:`bool`
        """
        if isinstance(matchers, (list, tuple)):
            self.matchers = list(matchers)
        else:
            self.matchers = [matchers]

        if isinstance(transformations, (list, tuple)):
            self.transformations = transformations
        else:
            self.transformations = [transformations]

    def match(self, visitor_state):
        """
        Iterates through the matchers
        """
        for m in self.matchers:
            if m(visitor_state.path):
                return self.transformations


class Matcher(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, visitor_state):
        pass

class QueryMatcher(Matcher):
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
    def __call__(self, visitor_state):
        """
        :param visitor_state: current parse state
        :returns: ``True`` if we have a match
        """
        if self.path_matcher:
            path = visitor_state.path
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

class Transformation(object):
    def transform_node(self, schema_node):
        """
        Mutates the :class:`schema.Node`.
        """
        pass

class AssignID(Transformation):
    """
    Transformation that applies an id to a node which will also break it out
    into a separate structure
    """
    def __init__(self, id):
        self.id = id

    def transform_node(self, schema_node):
        schema_node.id = self.id


def match_rule(path_query, assign_id):
    return Rule(QueryMatcher(path_query), AssignID(assign_id))
