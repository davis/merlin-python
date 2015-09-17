#!/usr/bin/env python
from __future__ import print_function
from itertools import islice
import sys
import argparse
import json

from merlin import Merlin, Uploader
from merlin.search import Search
from merlin.filter import Field, NF
from merlin.upload import Add, Update, Delete

def add_creds(parser):
    parser.add_argument("--username", required=True,
            help="Username credential")
    parser.add_argument("--authtoken", required=True,
            help="Authentication token")

def add_doc_group(parser, verb):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json-docs", dest="jDocs", nargs="+", type=jtype,
            help="Documents to %s, in json format" % verb)
    group.add_argument("--file", dest="inFile",
            help="File containing documents in json format, one per line, to %s" % verb)

def add_batch(parser):
    parser.add_argument("--batch-size", dest="batchSize", default=1000, type=int,
            help="Batch size for large scale operations")

def add_all(parser, verb):
    add_creds(parser)
    add_doc_group(parser, verb)
    add_batch(parser)
    
def jtype(d):
    return json.loads(d)

def build_arg_parser():
    parser = argparse.ArgumentParser(description='Command line tool for managing search')
    parser.add_argument("--instance", dest="instance", required=True,
            help="Full instance name: eg. blackbird.dev.foobar")

    parser.add_argument("--host", dest="host", 
            help="Host to use.  If omitted, uses default.")
    parser.add_argument("--no-ssl", dest="use_ssl", action="store_false",
            help="Use plain http")

    # Sub commands
    subparsers = parser.add_subparsers(dest='command',
            help="Available merlin CRUD operations")
    
    # Delete
    delete = subparsers.add_parser("delete", help="Delete a set of documents")
    add_all(delete, 'delete')

    # Update
    update = subparsers.add_parser("update", help="Update a set of documents")
    add_all(update, 'update')

    # Add
    add = subparsers.add_parser("add", help="Adds a set of documents")
    add_all(add, 'add')

    # Search
    search = subparsers.add_parser("read", help="Reads all the fields for a "\
            "given set of documents")

    search.add_argument("--docs", dest="docs", nargs="+", required=True,
            help="Document IDs")
    search.add_argument("--fields", dest="fields", nargs="+",
            help="Fields to retrieve")
    search.add_argument("--in-order", dest="inOrder", action="store_true", 
            help="Whether or not to return the results in order")

    return parser

def pprint(data):
    return json.dumps(data,sort_keys=True, indent=2, separators=(',', ': '))

def read(args):
    company, env, instance = args.instance.split('.')

    engine = Merlin(company, env, instance, 
            host=args.host, use_ssl=args.use_ssl)

    docs = args.docs if not args.inOrder else [[d] for d in args.docs]
    for docSet in docs:
        s = Search(
            filter=NF.cnf(Field('id') == docSet),
            fields=args.fields
        )
        with engine(s) as results:
            for hit in results.hits:
                print(pprint(hit))

def readDocs(args):
    if args.jDocs is not None:
        for d in args.jDocs:
            yield d

    elif args.inFile == '-':
        for line in sys.stdin:
            yield json.loads(line)

    else:
        with file(args.inFile) as f:
            for line in f:
                yield json.loads(line)

def batch(iterable, size):
    it = iter(iterable)
    sliceit = lambda it: list(islice(it, size))
    data = sliceit(it)
    while data:
        yield data
        data = sliceit(it)

def cud(args):
    """
    Create, Update, Delete
    """
    company, env, instance = args.instance.split('.')
    engine = Uploader(company, env, instance, 
        username=args.username,
        authtoken=args.authtoken,
        host=args.host, 
        use_ssl=args.use_ssl
    )

    bs = args.batchSize
    method = ({"add": Add, "update": Update, "delete": Delete})[args.command]
    for i, docs in enumerate(batch(readDocs(args), bs)):
        op = method()
        for doc in docs:
            print(doc)
            op += doc

        with engine(op) as results:
            if not results.success:
                error = "Error processing documents %s-%s" % (i * bs, (i + 1) * bs)
                print(error, file=sys.stderr)
                print(results.msg, file=sys.stderr)
                sys.exit(1)

            else:
                print(results.msg)

if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    if args.command == 'read':
        read(args)
    else:
        cud(args)
