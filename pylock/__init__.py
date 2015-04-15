# encoding: utf-8
"""Module holds methods and classes related to lock management"""
import os
import time

from cached_property import cached_property
from logging_utils import getLogger

from .states import LockState

logger = getLogger(__name__)

class BaseError(RuntimeError):
    """ Base error class for all errors raised from within this package """
    pass

class CouldNotCreateLockError(RuntimeError):
    """Error class raised when lock could not be created"""

    def __init__(self):
        super(CouldNotCreateLockError, self).__init__('Could not create lock')


class AlreadyLockedError(BaseError):
    """Error class that tells requested lock is unavailable by other
    instance """

    def __init__(self):
        super(AlreadyLockedError, self).__init__('Requested lock has been already acquired')


class Lock(object):
    """Class that represents single lock """

    def __init__(self, strategy, max_age=None, tries=3, sleeptime=2,
                 delay_provider=time.sleep, current_time_provider=time.time,
                 signal_submitter=os.kill):
        """ Object initialization

        :param strategy: lock strategy that performs locking
        :type strategy: pylock.strategy.Base
        :param max_age: Time after which other instance will break lock
        :type max_age: int
        :param tries: max number of tries to obtain lock
        :type tries: int
        :param sleeptime: sleep time between consecutiwe tries to obtain lock
        :type sleeptime: int
        """
        super(Lock, self).__init__()

        self._strategy = strategy
        self._max_age = max_age
        self._tries = tries
        self._sleeptime = sleeptime
        self._delay_provider = delay_provider
        self._current_time_provider = current_time_provider
        self._signal_submitter = signal_submitter

    @cached_property
    def pid(self):
        return os.getpid()

    @property
    def has_lock(self):
        """Returns information whether lock has been acquired or not

        :rtype: bool
        """
        return self._get_lock_state().is_owner

    def acquire(self):
        """ Method acquires lock

        :returns: lock state information
        :rtype: pylock.states.LockState
        :raises CouldNotCreateLockError: when lockfile could not be written
                                            (but was supposed to)
        """
        if not self.has_lock:
            return self._acquire()
        return LockState.OWNER

    def _acquire(self):
        """ Method actually tries to acquire lock

        :returns: acquire status
        :rtype: int
        :raises CouldNotCreateLockError: when lockfile could not be written
                                            (but was supposed to)
        """
        locktries = self._tries
        while locktries > 0:
            locktries -= 1
            try:
                state = self._do_lock()
                if state.is_owner:
                    return state
            except CouldNotCreateLockError:
                if locktries > 0:
                    self._delay_provider(self._sleeptime)
                else:
                    raise
        return LockState.LOCKED

    def _do_lock(self):
        """ Performs current lock validation and obtains new lock if possible

        :returns: None
        :raise CouldNotCreateLockError: lock could not be created but was \
                                        supposed to
        """
        state = self._get_lock_state()

        if not state.can_acquire:
            return state

        if state.should_kill_old_process:
            self._kill_old_process()

        print state
        if state.should_clean:
            self._strategy.clean()

        if not self._strategy.create(self.pid):
            raise CouldNotCreateLockError()

        return LockState.OWNER

    def _get_lock_state(self):
        """Method checks whether lock can be acquired.

        :returns: True if lock can be acquired, False if not.
                    Raises exception if lock has been already acquired
        :rtype: pylock.states.LockState
        """

        if not self._strategy.is_valid():
            return LockState.INVALID

        if not self._strategy.exists():
            return LockState.UNLOCKED

        if self._i_own_lock():
            return LockState.OWNER

        if not self._is_pid_owner_working():
            return LockState.ORPHANED

        if self._is_outdated():
            return LockState.OUTDATED

        return LockState.LOCKED

    def _is_pid_owner_working(self):
        pid = self._strategy.read_pid()
        with logger.context(pid=pid):
            logger.debug('checking pid owner')
            try:
                self._signal_submitter(pid, 0)
                logger.debug('pid owner is working')
                return True
            except (OSError, TypeError):
                logger.debug('pid owner does not work')
            return False

    def _i_own_lock(self):
        return self._strategy.read_pid() == self.pid

    def _is_outdated(self):
        if self._max_age is None:
            return False

        return self._current_time_provider() - self._strategy.get_create_date() > self._max_age

    def _kill_old_process(self):
        self._signal_submitter(self._strategy.read_pid(), 9)

    def release(self):
        """ Method releases previously acquired lock
        Does nothing if no lock has been acquired

        :returns: instance of self
        :rtype: mapnocc.lockfile.Lockfile
        """
        if self.has_lock:
            self._strategy.clean()
        return self

    def __enter__(self):
        if not self.acquire().is_owner:
            raise AlreadyLockedError()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

