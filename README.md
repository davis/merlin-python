# Merlin Python Library

The Merlin Python library provides a python interface to the Blackbird search engine.

# Installation

- `python setup.py install`

Or, in a virtualenv:
- `virtualenv /path/to/venv`
- `source /path/to/venv/bin/activate`
- `python setup.py install`

# Testing / Contributing

1. Run tests using `python setup.py test`
2. Add tests for new features / bug fixes
3. Commit and issue a pull

## Documentation

View the `examples/` folder for usages.

Alternatively, view the `tests/` directory for lists of commonly used features.

http://www.blackbird.am/docs will be updated with additional examples.

## Binaries
Merlin comes with two executables to make it easy to fire one-offs from the commandline: mcrud.py and a wrapper, murl.py

### mcrud.py
mcrud.py allows a user to run four basic operations: add, read, update, and delete.

    # Reading example
    mcrud.py --instance 'company.env.endpoint' read --docs '{"id": 123}'

    # Data modifications require credentials to use
    mcrud.py --instance 'company.env.endpoint' delete --username "foo@company.com" --authtoken "bar123" --doc-ids 123 456 789

mcrud.py can take multiple forms of inputs for add, delete, and update:

    # Documents specified on the commandline
    mcrud.py --instance 'company.env.endpoint' add --username "foo@company.com" --authtoken "bar123" --json-docs '{"id": "123", "title": "test!"}' '{"id": "456", "title": "test two!"}'

    # Documents specified froma file or stdin.  Documents are line delimited
    mcrud.py --instance 'company.env.endpoint' update --username "foo@company.com" --authtoken "bar123" --file documents.json

    # To read from stdin, use '-' for the filename
    cat documents.json | mcrud.py --instance 'company.env.endpoint' update --username "foo@company.com" --authtoken "bar123" --file -

    # Adding large numbers of documents are automatically batched uploaded by 1000.
    # However, if the document size is large, it can be adjusted with the 
    # --batch-size parameter
    mcrud.py --instance 'company.env.endpoint' add --username "foo@company.com" --authtoken "bar123" --file documents.json --batch-size 500

### murl.py
murl.py is simply a wrapper around mcrud.py that fills out the above fields from the url in merlin admin:

    murl.py 'https://upload-dev.search.blackbird.am/add?instance_name=foo&token=123456789ABCDEF&user=you@company.com&env=dev&company_id=company' --file documents.json


