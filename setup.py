#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os.path

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

readme = read_md('README.md')

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'sanic==0.7.0'
]

test_requirements = [
    'pytest==3.2.0',
    'prospector==0.12.7',
    'pytest-sanic==0.1.6'
]

extras = {
    'test': test_requirements + requirements
}

# get version
metadata = {}
version_filename = os.path.join(os.path.dirname(__file__), 'sanicargs','__version__.py')
exec(open(version_filename).read(), None, metadata)

setup(
    name='sanicargs',
    version=metadata['__version__'],
    description="Parses query args in sanic using type annotations",
    long_description=readme + '\n\n' + history,
    author="jgv",
    author_email='jgv@trustpilot.com',
    url='https://github.com/trustpilot/python-sanicargs',
    packages=[
        'sanicargs',
    ],
    package_dir={'sanicargs':
                 'sanicargs'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='sanicargs sanic query args type annotations',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    extras_require=extras,

)
