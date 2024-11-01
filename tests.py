import os
import random
import unittest
import unittest.mock
from pathlib import Path
from tempfile import TemporaryDirectory

import artifactcache


def create_envvar_name():
    return "TEST_" + hex(random.randint(0, 0xFFFFFFFFFFFF))[2:]


class TestCacheWithEnv(unittest.TestCase):

    def setUp(self):
        self.envname = create_envvar_name()

    def tearDown(self):
        os.environ.pop(self.envname, default=None)

    def create_cache(self, path):
        return artifactcache.CacheWithEnv(path, self.envname, initialize_if_missing=False)

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


class TestSwitchableCacheAggregate(unittest.TestCase):

    def test_empty(self):
        empty = artifactcache.SwitchableCacheAggregate()
        # Verify no exceptions occur:
        empty.enable()
        self.assertTrue(empty.is_enabled())
        empty.disable()

    def test_nested_aggreagate(self):
        mockcache = unittest.mock.Mock()
        mockcache.is_enabled.return_value = False
        inner = artifactcache.SwitchableCacheAggregate(cache=mockcache)
        outer = artifactcache.SwitchableCacheAggregate(cache=inner)
        with self.subTest("enable/disable through aggregate"):
            self.assertFalse(outer.is_enabled())
            mockcache.is_enabled.assert_called_once()
            outer.enable()
            mockcache.enable.assert_called_once()
            mockcache.is_enabled.return_value = True
            self.assertTrue(outer.is_enabled())
            self.assertTrue(inner.is_enabled())
            outer.disable()
            mockcache.disable.assert_called_once()
            mockcache.is_enabled.return_value = False
            self.assertFalse(outer.is_enabled())
            self.assertFalse(inner.is_enabled())
        mockcache.reset_mock()
        with self.subTest("enable externally, disable through aggregate"):
            mockcache.is_enabled.return_value = True
            self.assertTrue(outer.is_enabled())
            self.assertTrue(inner.is_enabled())
            mockcache.is_enabled.assert_called()
            mockcache.enable.assert_not_called()
            outer.disable()
            mockcache.disable.assert_called_once()
            mockcache.is_enabled.return_value = False
            self.assertFalse(outer.is_enabled())
            self.assertFalse(inner.is_enabled())

    def test_full(self):
        mockcache = unittest.mock.Mock()
        mockcache.is_enabled.return_value = True
        envcache = artifactcache.CacheWithEnv("", create_envvar_name(), initialize_if_missing=False)
        aggregate = artifactcache.SwitchableCacheAggregate(mock=mockcache, env=envcache)
        self.assertEqual(aggregate.caches["mock"], mockcache)
        self.assertEqual(aggregate.caches["env"], envcache)
        self.assertFalse(aggregate.is_enabled())
        mockcache.reset_mock()
        with self.subTest("enable/disable through aggregate"):
            aggregate.enable()
            self.assertTrue(aggregate.is_enabled())
            mockcache.is_enabled.assert_called_once()
            mockcache.enable.assert_called_once()
            self.assertTrue(envcache.is_enabled())
            aggregate.disable()
            self.assertFalse(aggregate.is_enabled())
            mockcache.disable.assert_called_once()
            self.assertFalse(envcache.is_enabled())
        mockcache.reset_mock()
        with self.subTest("enable externally, disable through aggregate"):
            envcache.enable()
            self.assertTrue(aggregate.is_enabled())
            mockcache.is_enabled.assert_called_once()
            mockcache.enable.assert_not_called()
            mockcache.is_enabled.return_value = False
            self.assertFalse(aggregate.is_enabled())
            self.assertTrue(envcache.is_enabled())
            aggregate.disable()
            self.assertFalse(aggregate.is_enabled())
            mockcache.disable.assert_called_once()
            self.assertFalse(envcache.is_enabled())


class TestCentralizedCache(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.parent_dir = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test(self):
        path = self.parent_dir / "test"
        self.assertFalse(path.exists())
        with artifactcache.centralized_cache(path) as cache:
            self.assertTrue(cache.is_enabled())
            self.assertEqual(cache.path, path)
            self.assertTrue(path.exists())
            from artifactcache.nltk import cache as NLTK_CACHE
            self.assertNotEqual(NLTK_CACHE.path.relative_to(path), NLTK_CACHE.path)
        self.assertFalse(cache.is_enabled())


if __name__ == "__main__":
    unittest.main()
