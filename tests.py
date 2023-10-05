import os
import random
import unittest

from artifactcache import *


class TestCacheWithEnv(unittest.TestCase):

    def setUp(self):
        self.envname = "TEST_" + hex(random.randint(0, 0xFFFFFFFFFFFF))[2:]

    def tearDown(self):
        os.environ.pop(self.envname, default=None)

    def test_no_previous_env(self):
        os.environ.pop(self.envname, default=None)
        cache = CacheWithEnv(__file__, self.envname)
        self.assertFalse(cache.is_enabled())
        self.assertNotIn(self.envname, os.environ)
        cache.enable()
        self.assertTrue(cache.is_enabled())
        self.assertIn(self.envname, os.environ)
        self.assertEqual(__file__, os.environ[self.envname])
        cache.disable()
        self.assertFalse(cache.is_enabled())
        self.assertNotIn(self.envname, os.environ)

    def test_with_previous_env(self):
        previous_value = "this should be in the env-variable"
        os.environ[self.envname] = previous_value
        cache = CacheWithEnv(__file__, self.envname)
        self.assertFalse(cache.is_enabled())
        self.assertIn(self.envname, os.environ)
        self.assertEqual(previous_value, os.environ[self.envname])
        cache.enable()
        self.assertTrue(cache.is_enabled())
        self.assertIn(self.envname, os.environ)
        self.assertEqual(__file__, os.environ[self.envname])
        cache.disable()
        self.assertFalse(cache.is_enabled())
        self.assertIn(self.envname, os.environ)
        self.assertEqual(previous_value, os.environ[self.envname])


if __name__ == "__main__":
    unittest.main()