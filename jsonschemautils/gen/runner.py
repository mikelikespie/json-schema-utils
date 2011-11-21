import argparse
import sys

import jsonschemautils.util
import jsonschemautils.gen.visitor as visitor
import jsonschemautils.metaschema
from jsonschemautils.metaschema import Schema

import json
import yaml

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', type=argparse.FileType('r'), nargs='?', metavar='INPUT_JSON', default=sys.stdin)
    parser.add_argument('-o', '--output-file',  type=argparse.FileType('w'), default=sys.stdout, metavar='JSON_FILE')

    return parser.parse_args()


def main():
    args = parse_args()
    jsonschemautils.util.setup_yaml()

    d = visitor.Document()

    root = jsonschemautils.metaschema.Schema(raw_json=json.load(args.input_file))

    for s, path in root.iterschemas():
        s.flatten_items()

    types = {}

    def break_to_type(path_name, id):
        if not isinstance(path_name, (tuple, list)):
            path_name = (path_name,)

        if id not in types:
            types[id] = Schema(id=id, type=set())
        for s, path in root.iterschemas():
            if len(path) >= len(path_name) and path[-len(path_name):] == path_name:
                s.to_ref(types[id])

    def break_items(parent_path_name, id):
        if id not in types:
            types[id] = Schema(id=id, type=set(['object']))
        for s, path in root.iterschemas():
            if len(path) >= 2 and path[-2] == parent_path_name and path[-1] == '[]':
                s.to_ref(types[id])

    break_to_type('user', 'User')
    break_to_type('location', 'Location')
    break_to_type('entities', 'TweetEntities')
    break_to_type(('entities', 'urls'), 'URLEntities')
    break_to_type(('entities', 'user_mentions'), 'UserMentions')
    break_to_type(('entities', 'hashtags'), 'Hashtags')
    break_items('#', 'Tweet')

    for s, path in root.iterschemas():
        s.flatten_items()

    # Reduce arrays of items into singel ones
    for s, path in root.iterschemas():
        if isinstance(s.type, set) and len(s.type) == 1:
            s.type = list(s.type)[0]

    for s, path in root.iterschemas():
        if isinstance(s.items, (set, list)) and len(s.items) == 1:
            s.items = list(s.items)[0]


    yaml.dump(dict(types=visitor.schema_repr(types), result=visitor.schema_repr(root)), args.output_file, indent=2)
