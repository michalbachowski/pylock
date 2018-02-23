# encoding: utf-8
""" Tests for mapnocc.lockfile module """

import errno
import os
import time
from pylock._compat import mock
import unittest
import tempfile

from pylock.strategy.file import File



class FileTest(unittest.TestCase):

    def setUp(self):
        self.atomic_writer = mock.MagicMock()
        (_, self.path) = tempfile.mkstemp('.pid', 'pylock_test_lockfile')
        self.strategy = File(self.path, self.atomic_writer)

    def tearDown(self):
        try:
            os.remove(self.path)
        except:
            pass

    def test_exists_checks_if_file_exists(self):
        self.assertTrue(self.strategy.exists())
        os.remove(self.path)
        self.assertFalse(self.strategy.exists())

    def test_create_uses_given_atomic_writer(self):
        self.strategy.create('foo_pid')
        self.atomic_writer.assert_called_once_with(self.path, 'foo_pid')

    def test_create_suppresses_any_exceptions(self):
        self.atomic_writer.side_effect = IOError()
        self.strategy.create('bar_pid')

        self.atomic_writer.side_effect = OSError()
        self.strategy.create('bar_pid')

        self.atomic_writer.side_effect = RuntimeError()
        self.strategy.create('bar_pid')

    def test_clean_removes_lock_file(self):
        self.assertTrue(self.strategy.exists())
        self.strategy.clean()
        self.assertFalse(self.strategy.exists())

    def test_clean_suppresses_OSError_when_file_is_missing(self):
        self.assertTrue(self.strategy.exists())
        self.strategy.clean()
        self.assertFalse(self.strategy.exists())
        self.strategy.clean()

    @mock.patch('pylock.strategy.file.os')
    def test_clean_does_not_suppress_OSError_differ_than_missing_file(self, os_mock):
        os_mock.remove.side_effect = OSError(errno.EPERM, 'EPERM')
        self.assertRaises(OSError, self.strategy.clean)

    def test_read_pid_returns_pid_from_file(self):
        with open(self.path, 'w') as stream:
            stream.write('123')

        self.assertEqual(123, self.strategy.read_pid())

    def test_read_pid_returns_None_when_file_does_not_exist(self):
        self.strategy.clean()
        self.assertIsNone(self.strategy.read_pid())

    def test_read_pid_returns_None_when_file_does_not_contain_integer(self):
        with open(self.path, 'w') as stream:
            stream.write('asd')
        self.assertIsNone(self.strategy.read_pid())

    def test_get_create_date_returns_time_when_pid_file_was_created(self):
        self.assertLessEqual(time.time() - self.strategy.get_create_date(), 1)

    @mock.patch('pylock.strategy.file.os')
    def test_get_create_date_returns_0_when_OSError_occurs(self, os_mock):
        os_mock.stat.side_effect = OSError(errno.EPERM, 'EPERM')
        self.assertEqual(0, self.strategy.get_create_date())
