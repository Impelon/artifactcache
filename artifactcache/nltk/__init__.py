from .._cachetypes import CacheWithEnv
from .._centralized_location import cache_path_for

__all__ = ["cache"]

cache = CacheWithEnv(cache_path_for(__file__), "NLTK_DATA")
