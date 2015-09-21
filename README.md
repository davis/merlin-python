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

# mcrud.py

Merlin python comes with an easy to use tool for running CRUD operations on your search index: mcrud.py

Command-line options can be viewed by add -h:

    mcrud.py -h
    mcrud.py add -h
    mcrud.py update -h
    mcrud.py delete -h
    mcrud.py read -h

### READ

    # Reads two documents from a provided instance's products table
    # No extra credentials are required
    mcrud.py --instance company.env.inst read --doc-ids f346904e7dcd43c521bff2e6dcfae21a c05ef333b5dbd9f31123a65221762395 --fields 'title,url,id'

### ADD, UPDATE, or DELETE
All data modifying actions require the use of authentication credentials:

    # Deleting
    mcrud.py --instance company.env.inst delete --username 'username@company.com' --authtoken 'authtoken' --doc-ids f346904e7dcd43c521bff2e6

Documents can be entered three ways:
    
    # Inline
    mcrud.py --instance company.env.inst update --username 'username@company.com' --authtoken 'authtoken' --json-docs '{"id": 123, "title": "red skirt"}'

    # From a file, with each line having a different json document
    mcrud.py --instance company.env.inst add --username 'username@company.com' --authtoken 'authtoken' --file new-products.json

    # From stdin, using '-' as the filename
    head -n 30 update-products.json | mcrud.py --instance company.env.inst add --username 'username@company.com' --authtoken 'authtoken' --file -

