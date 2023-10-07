"""Package to conveniently change the default download location for different
libraries."""

from ._cachetypes import *
from ._centralized_location import *
from ._version import package_version

__version__ = package_version
if package_version is None:
    __version__ = "unknown"
del package_version
