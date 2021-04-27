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
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/id-for-dummy-jpg')
        respx.get(mocked_url).mock(return_value=Response(200, json={ "_source": self._source }))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-for-dummy-jpg/raw.jpg')

        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-jpg.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.json(), { "previewable": True, "pages": 1, "content": None, "content_type": "image/jpeg" })


    @respx.mock
    def test_wrong_info_json(self):
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/id-wrong-jpg')
        respx.get(mocked_url).mock(return_value=Response(500, json={ "error": None }))
        response = self.client.get('/api/v1/thumbnail/my-index/id-wrong-jpg.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), { "previewable": False, "pages": 0 })


    @respx.mock
    def test_thumbnail_with_neither_cookie_nor_header(self):
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/id-unauthorized')
        respx.get(mocked_url).mock(return_value=Response(401))
        response = self.client.get('/api/v1/thumbnail/my-index/id-unauthorized')
        self.assertEqual(response.status_code, 401)


    @respx.mock
    def test_wrong_thunbnail_info(self):
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/id-wrong-jpg')
        respx.get(mocked_url).mock(return_value=Response(500, json={ "error": None }))
        response = self.client.get('/api/v1/thumbnail/my-index/id-wrong-jpg', headers=auth_headers())
        self.assertEqual(response.status_code, 403)


    @respx.mock
    def test_wrong_thunbnail_download(self):
        mocked_info_url = self.datashare_url('/api/index/search/my-index/_doc/id-for-dummy-jpg')
        respx.get(mocked_info_url).mock(return_value=Response(200, json={ "_source": self._source }))
        mocked_download_url = self.datashare_url('/api/my-index/documents/src/id-for-dummy-jpg')
        respx.get(mocked_info_url).mock(return_value=Response(500, json={ "error": None }))
        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-jpg', headers=auth_headers())
        self.assertEqual(response.status_code, 403)
