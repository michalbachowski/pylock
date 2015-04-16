# encoding: utf-8
""" Tests for pylock.strategy.file.writers module """

import os
import unittest
import tempfile

from pylock.strategy.file.writers import atomic_write

try:
    import atomicwrites
    has_atomic_writes = True
except ImportError:
    has_atomic_writes = False

class AtomicWriteTest(unittest.TestCase):

    def setUp(self):
        (_, self.path) = tempfile.mkstemp('.pid', 'pylock_test_atomic_write')

    def tearDown(self):
        try:
            os.remove(self.path)
        except:
            pass

    @unittest.skipUnless(has_atomic_writes, 'atomicwrites package is missing')
    def test_when_atomicwrites_package_is_present_and_file_does_not_exist_data_is_written(self):
        os.remove(self.path)
        atomic_write(self.path, 'foo')
        with open(self.path, 'r') as stream:
            self.assertEqual('foo', stream.readline())

    @unittest.skipUnless(has_atomic_writes, 'atomicwrites package is missing')
    def test_when_atomicwrites_package_is_present_and_file_exists_data_are_not_written(self):
        with self.assertRaises(OSError):
            atomic_write(self.path, 'bar')

    @unittest.skipIf(has_atomic_writes, 'atomicwrites package is missing')
    def test_when_atomicwrites_package_is_no_present_NotImplementedError_is_raised(self):
        self.assertRaises(NotImplementedError, atomic_write, self.path, 'baz')

