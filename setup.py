#!/usr/bin/env python

from setuptools import setup
from distutils.core import setup

import merlin

setup(name='py-merlin',
      version=merlin.__version__,
      description='Python bindings for Blackbird Search',
      url="https://github.com/blackbirdtech/merlin-python",
      packages=['merlin', 'merlin/upload'],
      scripts=['bin/mcrud.py'],
      test_suite='tests',
      install_requires=[
          # See requirements.txt
      ],
      author='Blackbird Technologies')
