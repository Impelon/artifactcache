"""Enabling this cache only works before the transformers-package has been
(re-)imported."""

import os.path

from ...__init__ import CacheWithEnv

__all__ = ["cache"]

cache = CacheWithEnv(os.path.dirname(os.path.realpath(__file__)), "TRANSFORMERS_CACHE")
