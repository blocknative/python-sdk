#!/usr/bin/env python

import ast
import os
import re
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('blocknative/__init__.py', 'rb') as f:
    print('version')
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('README.md') as readme_file:
    README = readme_file.read()

setup(
    name='blocknative-sdk',
    version=version,
    description='',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Taylor Dawson',
    author_email='taylor@blocknative.com',
    url='https://github.com/blocknative/python-sdk',
    keywords='ethereum,api,transactions,blocknative',
    package_dir={"": "blocknative"},
    packages=find_packages(where="blocknative"),
)