# encoding: utf-8
""" Module holds methods and classes related to manage file-based locks """
import os
import errno

from logging_utils import getLogger
from logging_utils.sentinel import SentinelBuilder

from pylock.strategy import Base

logger = getLogger(__name__)
sentinel = SentinelBuilder(logger, reraise=False, with_traceback=False)

class File(Base):
    """Class that represents file-based locking strategy (PID file)"""

    def __init__(self, path, atomic_writer=None):
        """ Object initialization

        :param path: path to lockfile
        :type path: str
        """
        super(File, self).__init__()

        self._path = path
        self._atomic_writer = atomic_writer

    def exists(self):
        return os.path.exists(self._path)

    def create(self, pid):
        """ Write the PID in the named PID file.

        Get the numeric process ID (“PID”) of the current process
        and write it to the named file as a line of text.

        :param pid: pid to be written
        :type pid: int
        """
        with sentinel('Create lockfile'):
            # sentinel will catch any exception, log message and suppress it
            self._atomic_writer(self._path, str(pid))
            return True
        return False

    def clean(self):
        """ Remove the named PID file if it exists.

        :returns: None
        :rtype: None
        """
        with logger.context(pidfile=self._path):
            try:
                logger.debug('removing pidfile')
                os.remove(self._path)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    logger.exception('could not remove pidfile')
                    raise

    def read_pid(self):
        """ Read the PID recorded in the named PID file.

        :returns: pid from pidfile
        :rtype: int
        """

        with logger.context(pidfile=self._path):
            logger.debug('reading pid from pidfile')
            try:
                pidfile = open(self._path, 'r')
            except IOError:
                logger.debug('could not read pid from pidfile')
                return

            logger.debug('parsing content from pidfile')
            try:
                return int(pidfile.readline().strip())
            except ValueError:
                logger.exception('could not parse pidfile content')
                pass
            finally:
                pidfile.close()

    def get_create_date(self):
        try:
            return os.stat(self._path).st_mtime
        except OSError:
            return 0

