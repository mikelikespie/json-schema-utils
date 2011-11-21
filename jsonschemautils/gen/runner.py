import argparse
import sys

import jsonschemautils.util
import jsonschemautils.gen.visitor as visitor
import jsonschemautils.metaschema

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

    for s, path in root.iterschemas():
        if isinstance(s.type, set) and len(s.type) == 1:
            s.type = list(s.type)[0]
    
    yaml.dump(visitor.schema_repr(root), args.output_file, indent=2)
