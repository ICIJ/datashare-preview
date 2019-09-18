import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer


def create_file_ondisk(path):
    pass


class ViewIntegrationTest(unittest.TestCase):
    httpd = None
    executor = None
    @classmethod
    def setUpClass(cls) -> None:
        cls.httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
        cls.executor = ThreadPoolExecutor(max_workers=1)
        cls.executor.submit(cls.httpd.serve_forever)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.httpd.shutdown()
        cls.executor.shutdown()

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

    def test_thumbnail_with_neither_cookie_nor_header(self):
        response = self.app.get('/api/v1/thumbnail/index/id', expect_errors=True)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_thumbnail_with_cookie(self):
        response = self.app.get('/api/v1/thumbnail/index/id', headers={'Cookie': '_ds_session_id={"login":"userid","roles":[],"sessionId":"eb43162397eddfb31da1255dcb16643c","redirectAfterLogin":"/"}'})
        self.assertEqual(response.status, '200 OK')

    def test_thumbnail_with_header(self):
        response = self.app.get('/api/v1/thumbnail/index/id', headers={'X-Ds-Session-Id': '{"login":"userid","roles":[],"sessionId":"eb43162397eddfb31da1255dcb16643c","redirectAfterLogin":"/"}'})
        self.assertEqual(response.status, '200 OK')

    def _assert_cors_headers_ok(self, response):
        self.assertEqual('*', response.headers.get('Access-Control-Allow-Origin'))
        self.assertEqual('GET', response.headers.get('Access-Control-Allow-Methods'))
        self.assertEqual('x-ds-session-id', response.headers.get('Access-Control-Allow-Headers'))


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Cookie') is None or '_ds_session_id' not in self.headers.get('Cookie'):
            self.send_error(401)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"_source": {"contentType": "text/plain", "path": "my_doc.txt", "contentLength": 123}}')
