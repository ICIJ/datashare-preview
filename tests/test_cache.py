import datetime
import subprocess
import os
import unittest

from dspreview.cache import DocumentCache, CACHE_PATH
from tempfile import gettempdir


def seconds_ago(n):
    return datetime.datetime.now() - datetime.timedelta(seconds = n)


def makedirs_seconds_ago(path, n = 0):
    os.makedirs(path, exist_ok = True)
    n_seconds_ago = seconds_ago(n).strftime('%Y%m%d%H%M.%S')
    subprocess.run(['touch', path, '-t', n_seconds_ago])


class CacheTest(unittest.TestCase):

    def test_cache_is_purged(self):
        target = os.path.join(CACHE_PATH, 'documents/test-index/to-delete-id/')
        makedirs_seconds_ago(target, 1000)
        self.assertTrue(os.path.exists(target))
        DocumentCache(999).purge()
        self.assertFalse(os.path.exists(target))

    def test_cache_is_not_purged(self):
        target = os.path.join(CACHE_PATH, 'documents/test-index/not-to-delete-id/')
        makedirs_seconds_ago(target, 10)
        self.assertTrue(os.path.exists(target))
        DocumentCache(999).purge()
        self.assertTrue(os.path.exists(target))
