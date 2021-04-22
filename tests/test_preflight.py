import json

from .test_abstract import auth_headers, create_file_ondisk_from_resource
from .test_abstract import AbstractTest


class PreflightTest(AbstractTest):

    def assert_cors_headers_ok(self, response):
        self.assertEqual('*', response.headers.get('access-control-allow-origin'))
        self.assertEqual('true', response.headers.get('access-control-allow-credentials'))

    def test_cors_thumbnail_preflight(self):
        headers = { 'Origin': 'http://localhost' }
        self.assert_cors_headers_ok(self.client.options('/api/v1/thumbnail/index/id', headers=headers))

    def test_cors_info_preflight(self):
        headers = { 'Origin': 'http://localhost' }
        self.assert_cors_headers_ok(self.client.options('/api/v1/thumbnail/index/id.json', headers=headers))
