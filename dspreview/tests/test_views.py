import json
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from shutil import copyfile

def create_jpeg_ondisk(path):
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources/dummy.jpg'), path)

def create_ods_ondisk(path):
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources/dummy.ods'), path)

def create_csv_ondisk(path):
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources/dummy.csv'), path)

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
        create_jpeg_ondisk('/tmp/ds-preview--index-id')
        response = self.app.get('/api/v1/thumbnail/index/id', headers=auth_headers())
        self.assertEqual(response.status, '200 OK')

    def test_thumbnail_with_header(self):
        create_jpeg_ondisk('/tmp/ds-preview--index-id')
        response = self.app.get('/api/v1/thumbnail/index/id', headers=auth_headers())
        self.assertEqual(response.status, '200 OK')

    def test_info_json(self):
        create_jpeg_ondisk('/tmp/ds-preview--index-id')
        response = self.app.get('/api/v1/thumbnail/index/id.json', headers=auth_headers())
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(json.loads(response.body.decode()), {"previewable": True, "pages": 1, "content": None, "content_type": "image/jpeg"})

    def test_ods_json_has_sheets(self):
        create_ods_ondisk('/tmp/ds-preview--index-id')
        response = self.app.get('/api/v1/thumbnail/index/id.json?include-content=1', headers=auth_headers())
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        info = json.loads(response.body.decode())
        self.assertIn('people', info['content'])
        self.assertIn('meals', info['content'])

    def test_ods_json_has_first_sheet(self):
        create_ods_ondisk('/tmp/ds-preview--index-id')
        response = self.app.get('/api/v1/thumbnail/index/id.json?include-content=1', headers=auth_headers())
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        info = json.loads(response.body.decode())
        self.assertEqual(len(info['content']['people']), 2)
        self.assertEqual(info['content']['people'][0][0], 'firstname')
        self.assertEqual(info['content']['people'][0][1], 'lastname')
        self.assertEqual(info['content']['people'][1][0], 'foo')
        self.assertEqual(info['content']['people'][1][1], 'bar')

    def test_ods_json_has_second_sheet(self):
        create_ods_ondisk('/tmp/ds-preview--index-id')
        response = self.app.get('/api/v1/thumbnail/index/id.json?include-content=1', headers=auth_headers())
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        info = json.loads(response.body.decode())
        self.assertEqual(len(info['content']['meals']), 4)
        self.assertEqual(info['content']['meals'][0][0], 'name')
        self.assertEqual(info['content']['meals'][1][0], 'couscous')
        self.assertEqual(info['content']['meals'][2][0], 'hummus')
        self.assertEqual(info['content']['meals'][3][0], 'paella')

    def _assert_cors_headers_ok(self, response):
        self.assertEqual('*', response.headers.get('Access-Control-Allow-Origin'))
        self.assertEqual('GET', response.headers.get('Access-Control-Allow-Methods'))
        self.assertEqual('x-ds-session-id', response.headers.get('Access-Control-Allow-Headers'))

def auth_headers():
    return {'Cookie': '_ds_session_id={"login":"userid","roles":[],"sessionId":"sid","redirectAfterLogin":"/"}'}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Cookie') is None or '_ds_session_id' not in self.headers.get('Cookie'):
            self.send_error(401)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"_source": {"contentType": "text/plain", "path": "my_doc.txt", "contentLength": 123}}')
