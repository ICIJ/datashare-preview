import unittest


class ViewIntegrationTest(unittest.TestCase):
    def setUp(self):
        from dspreview import main
        app = main({})
        from webtest import TestApp

        self.app = TestApp(app)

    def test_home_page(self):
        response = self.app.get('/')
        self.assertIn(b'Datashare preview', response.body)

    def test_cors_thumbnail_preflight(self):
        self._assert_cors_headers_ok(self.app.options('/api/v1/thumbnail/index/id'))

    def test_cors_info_preflight(self):
        self._assert_cors_headers_ok(self.app.options('/api/v1/thumbnail/index/id.json'))

    def _assert_cors_headers_ok(self, response):
        self.assertEqual('*', response.headers.get('Access-Control-Allow-Origin'))
        self.assertEqual('GET', response.headers.get('Access-Control-Allow-Methods'))
        self.assertEqual('x-ds-session-id', response.headers.get('Access-Control-Allow-Headers'))