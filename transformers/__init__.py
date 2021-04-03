"""
Enabling this cache only works before the transformers-package has been (re-)imported.
"""

from ..__init__ import CacheWithEnv

import os.path

CACHE = CacheWithEnv(os.path.dirname(os.path.realpath(__file__)), "TRANSFORMERS_CACHE")

path = CACHE.path
is_enabled = CACHE.is_enabled
enable = CACHE.enable
disable = CACHE.disable
