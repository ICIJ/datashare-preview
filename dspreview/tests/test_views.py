import unittest

from pyramid import testing
from pyramid.testing import DummyRequest

from dspreview.views import home


class ViewTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_home_page(self):
        self.assertIn(b"Datashare preview", home(DummyRequest()).body)