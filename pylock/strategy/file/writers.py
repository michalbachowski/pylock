# encoding: utf-8

from __future__ import absolute_import

try:
    from atomicwrites import atomic_write as atomic_write_
except ImportError:
    atomic_write_ = None


def atomic_write(path, data):
    if atomic_write_ is None:
        raise NotImplementedError('atomicwrites.atomic_write is missing')

    with atomic_write_(path, overwrite=False) as stream:
        stream.write(data)

