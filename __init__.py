"""Just a slightly hacky solution to make importing the top-level directory
behave the same as importing the package.

This is mainly intended to allow using this library from within a git
submodule instead of a pip installation.
"""

from .artifactcache import __path__, __version__
from .artifactcache import *
