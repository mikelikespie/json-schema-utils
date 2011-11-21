"""
Rule based matching and transforming
"""

import re
import itertools
import abc
from collections import namedtuple

SEP_TOKEN = '@@'

VisitorState = namedtuple('VisitorState', 'root_node current_path current_node')


class Rule(object):
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

    def __call__(self, visitor_state):
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


class MakeRef(object):
    """
    Transformation that applies an id to a node which will also break it out
    into a separate structure
    """
    def __init__(self, ref_id):
        self.id = ref_id

    def __call__(self, schema_node):
        schema_node.id = self.ref_id


def match_rule(path_query, assign_id):
    return Rule(QueryMatcher(path_query), AssignID(assign_id))
