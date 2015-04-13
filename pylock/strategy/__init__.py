# encoding: utf-8

import abc

class Base(abc.ABCMeta):

    def is_valid(self):
        return True

    @abc.abstractmethod
    def create(self, pid):
        pass # pragma: no cover

    @abc.abstractmethod
    def clean(self):
        pass # pragma: no cover

    @abc.abstractmethod
    def read_pid(self):
        pass # pragma: no cover

    @abc.abstractmethod
    def get_create_date(self, max_age):
        pass # pragma: no cover

