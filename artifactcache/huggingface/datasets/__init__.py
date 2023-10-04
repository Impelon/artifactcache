import os.path

from ...cachetypes import CacheWithEnv

__all__ = ["cache"]

cache = CacheWithEnv(os.path.dirname(os.path.realpath(__file__)), "HF_DATASETS_CACHE")