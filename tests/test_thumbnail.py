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

    _root_source = {
        "contentType": "application/pdf",
        "path": "dummy.pdf",
        "contentLength": 1234
    }

    _root_big_source = {
        "contentType": "application/pdf",
        "path": "dummy.pdf",
        "contentLength": 60000000
    }

    @respx.mock
    def test_info_json(self):
        mocked_url = self.document_url('my-index', 'id-for-dummy-jpg')
        respx.get(mocked_url).mock(return_value=Response(200, json={ "_source": self._source }))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-for-dummy-jpg/raw.jpg')

        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-jpg.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response.json().get("previewable"), True)
        self.assertTrue(response.json().get("pages"), 1)
        self.assertTrue(response.json().get("content_type"), "image/jpeg")

    @respx.mock
    def test_info_with_routing_json(self):
        mocked_root_url = self.document_url('my-index', 'rooting-id')
        respx.get(mocked_root_url).mock(return_value=Response(200, json={"_source": self._root_source}))

        mocked_url = self.document_url('my-index', 'id-for-dummy-jpg')
        respx.get(mocked_url).mock(return_value=Response(200, json={"_source": self._source}))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-for-dummy-jpg/raw.jpg')

        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-jpg.json?routing=rooting-id', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response.json().get("previewable"), True)
        self.assertTrue(response.json().get("pages"), 1)
        self.assertTrue(response.json().get("content_type"), "image/jpeg")

    @respx.mock
    def test_info_with_routing_too_big_json(self):
        mocked_root_url = self.document_url('my-index', 'rooting-id')
        respx.get(mocked_root_url).mock(return_value=Response(200, json={"_source": self._root_big_source}))

        mocked_url = self.document_url('my-index', 'id-for-dummy-jpg')
        respx.get(mocked_url).mock(return_value=Response(200, json={"_source": self._source}))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-for-dummy-jpg/raw.jpg')

        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-jpg.json?routing=rooting-id', headers=auth_headers())
        self.assertEqual(response.status_code, 413)

    @respx.mock
    def test_wrong_info_json(self):
        mocked_url = self.document_url('my-index', 'id-wrong-jpg')
        respx.get(mocked_url).mock(return_value=Response(500, json={ "error": None }))
        response = self.client.get('/api/v1/thumbnail/my-index/id-wrong-jpg.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), { "previewable": False, "pages": 0 })


    @respx.mock
    def test_thumbnail_with_neither_cookie_nor_header(self):
        mocked_url = self.document_url('my-index', 'id-unauthorized')
        respx.get(mocked_url).mock(return_value=Response(401))
        response = self.client.get('/api/v1/thumbnail/my-index/id-unauthorized')
        self.assertEqual(response.status_code, 401)


    @respx.mock
    def test_wrong_thunbnail_info(self):
        mocked_url = self.document_url('my-index', 'id-wrong-jpg')
        respx.get(mocked_url).mock(return_value=Response(500, json={ "error": None }))
        response = self.client.get('/api/v1/thumbnail/my-index/id-wrong-jpg', headers=auth_headers())
        self.assertEqual(response.status_code, 415)


    @respx.mock
    def test_wrong_thunbnail_download(self):
        mocked_info_url = self.document_url('my-index', 'id-for-dummy-jpg')
        respx.get(mocked_info_url).mock(return_value=Response(200, json={ "_source": self._source }))
        mocked_download_url = self.datashare_url('/api/my-index/documents/src/id-for-dummy-jpg')
        respx.get(mocked_info_url).mock(return_value=Response(500, json={ "error": None }))
        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-jpg', headers=auth_headers())
        self.assertEqual(response.status_code, 415)
