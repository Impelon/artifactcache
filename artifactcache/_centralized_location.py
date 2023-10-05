import os
from pathlib import Path

from ._cachetypes import CacheWithEnv

__all__ = ["centralized_cache"]

_PACKAGE_ROOT = Path(__file__).parent.resolve()
_ENVVAR_CENTRALIZED_CACHE = "ARTIFACTCACHE_CENTRAL_LOCATION"
os.environ[_ENVVAR_CENTRALIZED_CACHE] = str(_PACKAGE_ROOT)


def centralized_cache(path):
    return CacheWithEnv(path, _ENVVAR_CENTRALIZED_CACHE)


def cache_path_for(module_source_file):
    module_path = Path(module_source_file).parent.resolve()
    relative_module_path = module_path.relative_to(_PACKAGE_ROOT)
    location = Path(os.environ.get(_ENVVAR_CENTRALIZED_CACHE, default=_PACKAGE_ROOT)).resolve()
    return location / relative_module_path
