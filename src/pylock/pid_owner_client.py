# encoding: utf-8
import abc
import os
from logging_utils import getLogger
from logging_utils.sentinel import SentinelBuilder

from ._compat import with_metaclass

logger = getLogger(__name__)
sentinel = SentinelBuilder(logger)


class Client(with_metaclass(abc.ABCMeta)):

    def is_alive(self, pid):
        try:
            with logger.context(pid=pid), sentinel('Checking pid owner liveness'):
                return self._is_alive(pid)
        except:
            return False

    @abc.abstractmethod
    def _is_alive(self, pid):
        pass # pragma: no cover

    def terminate(self, pid):
        with logger.context(pid=pid), sentinel('Terminating pid owner'):
            return self._terminate(pid)

    @abc.abstractmethod
    def _terminate(self, pid):
        pass # pragma: no cover


class SubprocessClient(Client):

    def _is_alive(self, pid):
        os.kill(pid, 0)
        return True

    def _terminate(self, pid):
        os.kill(pid, 9)

