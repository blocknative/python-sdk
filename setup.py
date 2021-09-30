#!/usr/bin/env python

import ast
from os import path
import re
from setuptools import setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("blocknative/__init__.py", "rb") as f:
    print("version")
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

with open("README.md") as readme_file:
    README = readme_file.read()

# Read requirements.txt
with open(
    path.join(path.abspath(path.dirname(__file__)), "requirements.txt"),
    encoding="utf-8",
) as f:
    requirements = f.read().split("\n")

setup(
    name="blocknative-sdk",
    version=version,
    description="Blocknative's Python SDK.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Taylor Dawson",
    author_email="taylor@blocknative.com",
    url="https://github.com/blocknative/python-sdk",
    keywords="ethereum,api,transactions,blocknative",
    packages=["blocknative"],
    python_requires=">=3.9",
    install_requires=requirements,
)
