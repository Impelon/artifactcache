import os
import random
import unittest
from pathlib import Path

from artifactcache import *


class TestCacheWithEnv(unittest.TestCase):

    def setUp(self):
        self.envname = "TEST_" + hex(random.randint(0, 0xFFFFFFFFFFFF))[2:]

    def tearDown(self):
        os.environ.pop(self.envname, default=None)

    def create_cache(self, path):
        return CacheWithEnv(path, self.envname, initialize_if_missing=False)

    def test_no_previous_env(self):
        os.environ.pop(self.envname, default=None)
        for path in (__file__, Path(__file__)):
            with self.subTest(path_is_object=isinstance(path, Path)):
                cache = self.create_cache(path)
                self.assertFalse(cache.is_enabled())
                self.assertNotIn(self.envname, os.environ)
                cache.enable()
                self.assertTrue(cache.is_enabled())
                self.assertIn(self.envname, os.environ)
                self.assertEqual(str(path), os.environ[self.envname])
                cache.disable()
                self.assertFalse(cache.is_enabled())
                self.assertNotIn(self.envname, os.environ)

    def test_with_previous_env(self):
        previous_value = "this should be in the env-variable"
        os.environ[self.envname] = previous_value
        for path in (__file__, Path(__file__)):
            with self.subTest(path_is_object=isinstance(path, Path)):
                cache = self.create_cache(path)
                self.assertFalse(cache.is_enabled())
                self.assertIn(self.envname, os.environ)
                self.assertEqual(previous_value, os.environ[self.envname])
                cache.enable()
                self.assertTrue(cache.is_enabled())
                self.assertIn(self.envname, os.environ)
                self.assertEqual(str(path), os.environ[self.envname])
                cache.disable()
                self.assertFalse(cache.is_enabled())
                self.assertIn(self.envname, os.environ)
                self.assertEqual(previous_value, os.environ[self.envname])

    def test_switch_path_of_enabled_cache(self):
        path = __file__
        previous_value = os.environ.get(self.envname, default=None)
        cache = self.create_cache(path)
        self.assertFalse(cache.is_enabled())
        cache.enable()
        self.assertTrue(cache.is_enabled())
        self.assertEqual(str(path), os.environ[self.envname])
        path = Path(path).parent / "a" / "new" / "path"
        cache.path = path
        self.assertTrue(cache.is_enabled())
        self.assertEqual(str(path), os.environ[self.envname])
        cache.disable()
        self.assertFalse(cache.is_enabled())
        self.assertEqual(previous_value, os.environ.get(self.envname, default=None))


if __name__ == "__main__":
    unittest.main()
