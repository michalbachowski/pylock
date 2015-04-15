# encoding: utf-8
""" Tests for pylock.__init__ module """
import os
import mock
import unittest

from pylock import Lock, AlreadyLockedError, CouldNotCreateLockError
from pylock.strategy import Base
from pylock.states import LockState

class LockTest(unittest.TestCase):

    def setUp(self):
        self.lockfile = '/tmp/lockfile'
        self.strategy = mock.MagicMock(Base)
        self.strategy.is_valid.return_value = True
        self.strategy.create.return_value = True
        self.strategy.exists.return_value = False
        self.delay_provider = mock.MagicMock()
        self.signal_submitter = mock.MagicMock()
        self.current_time_provider = mock.MagicMock()
        self.max_age = 10

    @property
    def lock(self):
        return Lock(self.strategy, max_age=self.max_age,
                         delay_provider=self.delay_provider,
                         current_time_provider=self.current_time_provider,
                         signal_submitter=self.signal_submitter)

    def test_acquire_returns_LockState(self):
        self.assertIsInstance(self.lock.acquire(), LockState)

    def test_acquire_called_multiple_times_locks_only_once(self):
        lock = self.lock
        self.assertTrue(lock.acquire().is_owner)
        # lock exists
        self.strategy.exists.return_value = True
        # current app owns lock
        self.strategy.read_pid.return_value = lock.pid
        self.assertTrue(lock.acquire().is_owner)

        self.strategy.create.assert_called_once_with(lock.pid)

    def test_acquire_returns_LockState_indicating_failed_lock_when_lock_can_not_be_obtained(self):
        lock = self.lock
        # lock exists
        self.strategy.exists.return_value = True
        # other app owns lock
        self.strategy.read_pid.return_value = lock.pid + 1
        # lock is not outdated
        self.current_time_provider.return_value = 123
        self.strategy.get_create_date.return_value = 123 - self.max_age // 2

        self.assertFalse(lock.acquire().is_owner)
        self.assertFalse(lock.acquire().can_acquire)
        self.assertTrue(lock.acquire().is_locked)

    def test_acquire_raises_exception_when_lock_can_be_obtained_but_failed_to_create(self):
        self.strategy.create.return_value = False
        self.assertRaises(CouldNotCreateLockError, self.lock.acquire)

    def test_acquire_breaks_outdated_lock_and_kills_lock_owner(self):
        fake_pid = 99999999
        # lock exists
        self.strategy.exists.return_value = True
        # other app owns lock
        self.strategy.read_pid.return_value = fake_pid

        # but lock is outdated
        self.current_time_provider.return_value = 123
        self.strategy.get_create_date.return_value = 123 - self.max_age * 2

        self.assertTrue(self.lock.acquire().is_owner)
        self.strategy.clean.assert_called_once_with()

        self.signal_submitter.assert_has_calls(
            [mock.call(fake_pid, 0),
            mock.call(fake_pid, 9)])

    def test_acquire_with_max_age_not_set_assumes_lock_always_active(self):
        self.max_age = None
        fake_pid = 99999999

        # lock exists
        self.strategy.exists.return_value = True
        # other app owns lock
        self.strategy.read_pid.return_value = fake_pid

        # but lock is outdated
        self.current_time_provider.return_value = 123
        self.strategy.get_create_date.return_value = 12

        self.assertFalse(self.lock.acquire().is_owner)
        self.assertEqual(0, self.strategy.clean.call_count)

    def test_acquire_breaks_invalid_lock_and_kills_its_owner(self):
        self.strategy.is_valid.return_value = False
        self.assertTrue(self.lock.acquire().is_owner)

        self.strategy.clean.assert_called_once_with()

        self.signal_submitter.assert_called_once_with(self.strategy.read_pid.return_value, 9)

    def test_acquire_breaks_locks_from_non_existent_processes(self):
        # lock exists
        self.strategy.exists.return_value = True
        # other app owns lock
        self.strategy.read_pid.return_value = self.lock.pid + 1
        # but this app does not exist
        self.signal_submitter.side_effect = OSError()
        self.assertTrue(self.lock.acquire().is_owner)
        self.strategy.clean.assert_called_once_with()

    def test_release_removes_lock(self):
        # lock exists
        self.strategy.exists.return_value = True
        # current app owns lock
        self.strategy.read_pid.return_value = self.lock.pid

        self.assertIsInstance(self.lock.release(), Lock)

        self.strategy.clean.assert_called_once_with()

    def test_release_does_not_remove_lock_that_does_not_own(self):
        # other app owns lock
        self.strategy.read_pid.return_value = 999

        self.assertIsInstance(self.lock.release(), Lock)

        self.assertEqual(0, self.strategy.clean.call_count)

    def test_Lock_object_acts_as_context_manager(self):

        # noone owns lock
        self.strategy.read_pid.return_value = None

        # lock is not outdated
        self.current_time_provider.return_value = 123
        self.strategy.get_create_date.return_value = 123 - self.max_age // 2

        with self.lock as lock:
            self.strategy.exists.return_value = True
            self.strategy.create.assert_called_once_with(lock.pid)

            # current app owns lock
            self.strategy.read_pid.return_value = self.lock.pid

            self.assertTrue(lock.has_lock)

        self.strategy.clean.assert_called_once_with()

    def test_when_entering_context_AlreadyLocked_exception_is_raised_is_lock_can_not_be_obtained(self):

        # lock exists
        self.strategy.exists.return_value = True

        # other process owns lock
        self.strategy.read_pid.return_value = 99

        # lock is not outdated
        self.current_time_provider.return_value = 123
        self.strategy.get_create_date.return_value = 123 - self.max_age // 2

        with self.assertRaises(AlreadyLockedError):
            with self.lock:
                pass

