#!/usr/bin/env python
from __future__ import print_function
import os
import urlparse
import sys
import argparse

def build_arg_parser():
    parser = argparse.ArgumentParser(description='Command line tool for managing search')
    parser.add_argument("url", help="URL for the given action")

    parser.add_argument("extras", nargs=argparse.REMAINDER,
            help="Extra arguments to pass in")

    return parser

def process(args):
    parsed = urlparse.urlparse(args.url)

    new_args = ['mcrud.py']
    new_args.extend(['--host', parsed.netloc])
    if parsed.scheme == 'http':
        new_args.append('--no-ssl')

    qs = urlparse.parse_qs(parsed.query)

    inst_fields = ('company_id', 'env', 'instance_name')
    if not all(f in qs for f in inst_fields):
        raise ValueError("Missing one of: %s" % ', '.join(inst_fields))

    instance = '.'.join(qs[f][0] for f in inst_fields)

    new_args.extend(['--instance', instance])

    verb = parsed.path.lstrip('/')

    new_args.append(verb)

    if verb in ('update', 'add', 'delete'):
        auth_fields = ('user', 'token')
        if not all(f in qs for f in auth_fields):
            raise ValueError("Missing one of: %s" % ', '.join(auth_fields))

        new_args.extend(['--username', qs['user'][0]])
        new_args.extend(['--authtoken', qs['token'][0]])

    new_args.extend(args.extras)

    return new_args

if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    new_args = process(args)
    print(' '.join(new_args))
    os.execvp(new_args[0], new_args)
