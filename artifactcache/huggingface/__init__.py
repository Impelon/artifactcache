import importlib
import pkgutil

from .._cachetypes import CacheWithEnv, SwitchableCacheAggregate
from .._centralized_location import cache_path_for

__all__ = ["internal_cache", "cache"]

internal_cache = CacheWithEnv(cache_path_for(__file__), "HF_HOME")

submodule_caches = {}
for finder, name, is_package in pkgutil.iter_modules(__path__):
    submodule = importlib.import_module("." + name, __name__)
    if hasattr(submodule, "cache"):
        submodule_caches[name] = submodule.cache

cache = SwitchableCacheAggregate(internal_cache=internal_cache, **submodule_caches)
