# encoding: utf-8
from enum import Enum

class LockState(Enum):

    INVALID = (False, True, False, True, True)
    LOCKED = (True, False, False, False, False)
    UNLOCKED = (False, True, False, False, False)
    OWNER = (True, False, True, False, False)
    ORPHANED = (True, True, False, True, False)
    OUTDATED = (True, True, False, True, True)

    def __init__(self, is_locked, can_acquire, is_owner, should_clean, should_kill_old_process):
        self.is_locked = is_locked
        self.is_owner = is_owner
        self.should_clean = should_clean
        self.should_kill_old_process = should_kill_old_process
        self.can_acquire = can_acquire

