import json
import respx

from httpx import Response
from .test_abstract import auth_headers, create_file_ondisk_from_resource
from .test_abstract import AbstractTest

class ThumbnailTest(AbstractTest):

    _source = {
        "contentType": "image/jpeg",
        "path": "dummy.jpg",
        "contentLength": 123
    }

    @respx.mock
    def test_info_json(self):
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/dummy-jpg')
        respx.get(mocked_url).mock(return_value=Response(200, json={ "_source": self._source }))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/dummy-jpg/raw.jpg')

        response = self.client.get('/api/v1/thumbnail/my-index/dummy-jpg.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.json(), {"previewable": True, "pages": 1, "content": None, "content_type": "image/jpeg"})

    @respx.mock
    def test_thumbnail_with_neither_cookie_nor_header(self):
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/dummy-id')
        respx.get(mocked_url).mock(return_value=Response(401))
        response = self.client.get('/api/v1/thumbnail/my-index/dummy-id')
        self.assertEqual(response.status_code, 401)
