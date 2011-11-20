import argparse
import sys

import jsonschemautils.util
import jsonschemautils.gen.visitor as visitor

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

    v = visitor.DocumentVisitor()
    v.walk_document(json.load(args.input_file))
    
    yaml.dump(v.generated_schema, args.output_file, indent=2)
