"""
Package for storing models and data for different libraries locally.
"""

import os

class Cache:

    """
    Class for caches accessible via a path.
    """

    def __init__(self, path):
        self.path = path

    def _get_path(self):
        return self._path

    def _set_path(self, path):
        self._path = path

    path = property(lambda obj: obj._get_path(), lambda obj, arg: obj._set_path(arg), doc="The path to this cache.")

class AbstractSwitchableCache(Cache):

    """
    Abstract base class for caches that can be enabled and disabled.
    """

    def _set_path(self, path):
        super(AbstractSwitchableCache, self)._set_path(path)
        if self.is_enabled():
            self.disable()
            self.enable()

    def is_enabled(self):
        """
        Return whether this cache is set to be used.
        """
        pass

    def enable(self):
        """
        Set the path so this cache is used.
        """
        pass

    def disable(self):
        """
        Reset the path for the cache used to its original path.
        """
        pass

class CacheWithEnv(AbstractSwitchableCache):

    """
    Class for caches that are controlled via an environment-variable.
    """

    def __init__(self, path, environment_variable):
        self.environment_variable = environment_variable
        self._original_path = os.environ.get(self.environment_variable, None)
        super(CacheWithEnv, self).__init__(path)

    def is_enabled(self):
        return self.environment_variable in os.environ and os.environ[self.environment_variable] == self.path

    def enable(self):
        if self.is_enabled():
            return
        self._original_path = os.environ.get(self.environment_variable, None)
        os.environ[self.environment_variable] = self.path

    def disable(self):
        if not self.is_enabled():
            return
        if self._original_path is None:
            del os.environ[self.environment_variable]
        else:
            os.environ[self.environment_variable] = self._original_path
