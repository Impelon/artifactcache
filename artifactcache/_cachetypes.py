import os


class AbstractSwitchableCache:

    """Abstract base class for caches that can be enabled and disabled."""

    def is_enabled(self):
        """Return whether this cache is set to be used."""
        pass

    def enable(self):
        """Set the path so this cache is used."""
        pass

    def disable(self):
        """Reset the path for the cache used to its original path."""
        pass

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, *exception_information):
        self.disable()
        return False


class SwitchableCacheAggregate(AbstractSwitchableCache):

    """Class for controling multiple switchable caches as one singular
    entity."""

    def __init__(self, **switchable_caches):
        self.caches = dict(switchable_caches)
        super(SwitchableCacheAggregate, self)

    def is_enabled(self):
        return all(map(lambda cache: cache.is_enabled(), self.caches.values()))

    def enable(self):
        for cache in self.caches.values():
            cache.enable()

    def disable(self):
        for cache in self.caches.values():
            cache.disable()

    def __repr__(self):
        return "{}({})".format(type(self).__name__, ", ".join(n + "=" + repr(c) for n, c in self.caches.items()))


class AbstractPathCache:

    """Class for caches accessible via a path."""

    def __init__(self, path):
        self.path = path

    def _get_path(self):
        return self._path

    def _set_path(self, path):
        self._path = path

    path = property(lambda obj: obj._get_path(), lambda obj, arg: obj._set_path(arg), doc="The path to this cache.")


class AbstractSwitchablePathCache(AbstractPathCache, AbstractSwitchableCache):

    def _set_path(self, path):
        was_enabled = False
        try:
            # May fail if path not yet initialized.
            was_enabled = self.is_enabled()
        except BaseException:
            pass
        super(AbstractSwitchablePathCache, self)._set_path(path)
        if was_enabled:
            self.disable()
            self.enable()


class CacheWithEnv(AbstractSwitchablePathCache):

    """Class for caches that are controlled via an environment-variable."""

    def __init__(self, path, environment_variable):
        self.environment_variable = environment_variable
        self._original_path = os.environ.get(self.environment_variable, None)
        super(CacheWithEnv, self).__init__(path)

    def is_enabled(self):
        return self.environment_variable in os.environ and os.environ[self.environment_variable] == str(self.path)

    def enable(self):
        if self.is_enabled():
            return
        os.environ[self.environment_variable] = str(self.path)

    def disable(self):
        if not self.is_enabled():
            return
        if self._original_path is None:
            del os.environ[self.environment_variable]
        else:
            os.environ[self.environment_variable] = self._original_path

    def __repr__(self):
        return "{}({!r}, {!r})".format(type(self).__name__, str(self.path), self.environment_variable)
