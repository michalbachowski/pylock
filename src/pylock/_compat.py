# -*- coding: utf-8 -*-
"""
Python 2.7.x, 3.2+ compatability module.
"""
from __future__ import unicode_literals
import sys

is_py2 = sys.version_info[0] == 2

def with_metaclass(meta, *bases):
    """Create a base class with a metaclass.
    Taken from python's "six" package source code:

    http://pythonhosted.org/six/#six.with_metaclass
    """
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, b'temporary_class', (), {})

if not is_py2:
    # Python 3

    from unittest import mock
else:
    # Python 2

    import mock

