import os
import respx

from shutil import rmtree
from unittest.mock import patch

from httpx import Response
from dspreview.config import settings
from .test_abstract import auth_headers, create_file_ondisk_from_resource, read_resource
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

    @respx.mock
    def test_info_json_for_path_without_extension(self):
        source_without_extension = {**self._source, 'path': 'dummy'}
        mocked_url = self.document_url('my-index', 'id-for-dummy-without-extension')
        respx.get(mocked_url).mock(return_value=Response(200, json={'_source': source_without_extension}))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-for-dummy-without-extension/raw.jpg')

        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-without-extension.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('previewable'))

    def test_thumbnail_rejects_routing_with_path_traversal(self):
        response = self.client.get('/api/v1/thumbnail/my-index/some-id?routing=../../../traversal-target', headers=auth_headers())
        self.assertEqual(response.status_code, 400)
        self.assertFalse(os.path.exists('/traversal-target'))

    def test_thumbnail_rejects_parent_directory_id(self):
        response = self.client.get('/api/v1/thumbnail/my-index/%2E%2E', headers=auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_thumbnail_rejects_page_that_is_not_a_number(self):
        response = self.client.get('/api/v1/thumbnail/my-index/some-id?page=abc', headers=auth_headers())
        self.assertEqual(response.status_code, 422)

    @respx.mock
    def test_thumbnail_downloads_the_document(self):
        mocked_info_url = self.document_url('my-index', 'id-to-download')
        respx.get(mocked_info_url).mock(return_value=Response(200, json={'_source': self._source}))
        mocked_download_url = self.datashare_url('/api/my-index/documents/src/id-to-download')
        dummy_jpg_content = read_resource('dummy.jpg')
        respx.get(mocked_download_url).mock(return_value=Response(200, content=dummy_jpg_content))
        rmtree('/tmp/documents/my-index/id-to-download', ignore_errors=True)

        response = self.client.get('/api/v1/thumbnail/my-index/id-to-download', headers=auth_headers())
        self.assertEqual(response.status_code, 200)

    @respx.mock
    def test_thumbnail_rejects_too_big_download_without_content_length(self):
        source_without_length = {'contentType': 'image/jpeg', 'path': 'dummy.jpg'}
        mocked_info_url = self.document_url('my-index', 'id-too-big')
        respx.get(mocked_info_url).mock(return_value=Response(200, json={'_source': source_without_length}))
        mocked_download_url = self.datashare_url('/api/my-index/documents/src/id-too-big')
        respx.get(mocked_download_url).mock(return_value=Response(200, content=b'x' * 100))
        rmtree('/tmp/documents/my-index/id-too-big', ignore_errors=True)

        with patch.object(settings, 'ds_document_max_size', 10):
            response = self.client.get('/api/v1/thumbnail/my-index/id-too-big', headers=auth_headers())
        self.assertEqual(response.status_code, 413)
        self.assertFalse(os.path.exists('/tmp/documents/my-index/id-too-big/raw.jpg'))
