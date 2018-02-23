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

# try to import "mock" (built-in Py3, external module in Py2)
try:
    from unittest import mock as _mock
    mock = _mock
except ImportError:
# mock is required only for tests - it might not be available for regular use
    try:
        import mock
    except ImportError:
        pass

__all__ = ['mock']


