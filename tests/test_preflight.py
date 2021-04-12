import json

from .test_abstract import auth_headers, create_file_ondisk_from_resource
from .test_abstract import AbstractTest


class PreflightTest(AbstractTest):

    def test_cors_thumbnail_preflight(self):
        self.assert_cors_headers_ok(self.app.options('/api/v1/thumbnail/index/id'))

    def test_cors_info_preflight(self):
        self.assert_cors_headers_ok(self.app.options('/api/v1/thumbnail/index/id.json'))
