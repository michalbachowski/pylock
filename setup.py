#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = '0.0.1'


def read(fname):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), fname), 'r', 'utf-8').read()

readme = read('README.md')

setup(
    name = 'pylock',
    version = __version__,
    description = 'Configurable lock manager',
    long_description = readme,
    author = 'Michał Bachowski',
    author_email = 'michalbachowski@gmail.com',
    url = 'https://github.com/michalbachowski/pylock',
    packages = ['pylock', 'pylock.strategy', 'pylock.strategy.file'],
    license = "MIT",
    package_dir = {'pylock': 'pylock'},
    install_requires = [],
    dependency_links = [],
    zip_safe = True,
    keywords = 'locking',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

