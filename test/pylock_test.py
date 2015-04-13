# encoding: utf-8
""" Tests for lockfile module """
import os
import unittest
import time
import tempfile

from mapnocc.lockfile import (Lockfile, AlreadyLockedError, \
                              CouldNotWritePidfileError)

(_, lockfile) = tempfile.mkstemp('.pid', 'mapnocc_test_lockfile')

class FakeLock(object):

    def __init__(self, path):
        self.cmd = 'while [ 1 ]; do echo $! > %s; sleep 4; exit; done &'
        self.path = path

    def __enter__(self):
        os.system(self.cmd % self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.system("rm %s" % self.path)


class LockfileTest(unittest.TestCase):

    def tearDown(self):
        try:
            os.remove(lockfile)
        except:
            pass

    def test_acquire_called_multiple_times_returns_always_true(self):
        l = Lockfile(lockfile)
        self.assertTrue(l.acquire())
        self.assertTrue(l.acquire())

    def test_acquire_raises_exception_when_lock_can_not_be_obtained(self):
        with FakeLock(lockfile):
            time.sleep(1)
            l = Lockfile(lockfile, tries=1, sleeptime=1)
            self.assertRaises(AlreadyLockedError, l.acquire)

    def test_acquire_breaks_outdated_lock(self):
        with FakeLock(lockfile):
            # wait 2 seconds for file to expire
            time.sleep(2)
            l = Lockfile(lockfile, max_age=1, tries=1, sleeptime=1)
            self.assertTrue(l.acquire())

    def test_acquire_breaks_locks_from_non_existent_processes(self):
        with FakeLock(lockfile):
            # wait for fake subprocess to expire
            time.sleep(5)
            l = Lockfile(lockfile, max_age = 1000, tries=1, sleeptime=1)
            self.assertTrue(l.acquire())

    def test_acquire_raises_CouldNotWritePidfileError_when_file_could_not_be_written(self):
        l = Lockfile('/non/existent/path')
        self.assertRaises(CouldNotWritePidfileError, l.acquire)

    def test_release_removes_pidfile(self):
        l = Lockfile(lockfile)
        l.acquire()
        self.assertTrue(l.release())

    def test_release_does_not_complain_if_lock_file_does_not_exist(self):
        l = Lockfile('/non/existent.path')
        l.release()
        self.assertTrue(True)

    def test_release_does_not_remove_lock_owned_by_someoneelse(self):
        with FakeLock(lockfile):
            time.sleep(1)
            self.assertTrue(os.path.exists(lockfile))
            l = Lockfile(lockfile)
            l.release()
            self.assertTrue(os.path.exists(lockfile))
        self.assertFalse(os.path.exists(lockfile))

    def test_enter_acquires_lock_exit_releases_lock(self):
        with Lockfile(lockfile) as lock:
            self.assertTrue(lock.has_lock)
            self.assertTrue(os.path.exists(lockfile))
        self.assertFalse(os.path.exists(lockfile))
