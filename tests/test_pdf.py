import os
import respx

from shutil import rmtree
from subprocess import TimeoutExpired
from unittest.mock import patch

from httpx import Response
from dspreview.document import Document
from .test_abstract import auth_headers, create_file_ondisk_from_resource, read_resource
from .test_abstract import AbstractTest


class PdfTest(AbstractTest):

    _source = {
        "contentType": "application/vnd.oasis.opendocument.text",
        "path": "dummy.odt",
        "contentLength": 8892
    }

    _root_big_source = {
        "contentType": "application/pdf",
        "path": "dummy.pdf",
        "contentLength": 60000000
    }

    _session = 'sid'

    def mock_odt(self, id):
        cookies = {'_ds_session_id': self._session}
        respx.get(self.document_url('my-index', id), cookies=cookies).mock(return_value=Response(200, json={'_source': self._source}))
        src_url = self.datashare_url(f'/api/my-index/documents/src/{id}')
        respx.get(src_url, cookies=cookies).mock(return_value=Response(200, content=read_resource('dummy.odt')))
        rmtree(f'/tmp/documents/my-index/{id}', ignore_errors=True)

    @respx.mock
    def test_info_json_for_odt(self):
        respx.get(self.document_url('my-index', 'id-for-dummy-odt')).mock(return_value=Response(200, json={'_source': self._source}))
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-for-dummy-odt/raw.odt')
        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-odt.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['previewable'])
        self.assertEqual(response.json()['pages'], 1)

    @respx.mock
    def test_pdf_for_odt(self):
        self.mock_odt('id-odt-to-pdf')
        response = self.client.get('/api/v1/pdf/my-index/id-odt-to-pdf', headers={'Cookie': f'_ds_session_id={self._session}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    @respx.mock
    def test_pdf_with_session_header(self):
        self.mock_odt('id-odt-to-pdf-with-header')
        response = self.client.get('/api/v1/pdf/my-index/id-odt-to-pdf-with-header', headers={'X-Ds-Session-Id': self._session})
        self.assertEqual(response.status_code, 200)

    @respx.mock
    def test_pdf_rejects_jpeg_and_keeps_cache(self):
        jpeg_source = {"contentType": "image/jpeg", "path": "dummy.jpg", "contentLength": 123}
        respx.get(self.document_url('my-index', 'id-jpg-on-pdf')).mock(return_value=Response(200, json={'_source': jpeg_source}))
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-jpg-on-pdf/raw.jpg')
        response = self.client.get('/api/v1/pdf/my-index/id-jpg-on-pdf', headers=auth_headers())
        self.assertEqual(response.status_code, 415)
        self.assertTrue(os.path.exists('/tmp/documents/my-index/id-jpg-on-pdf/raw.jpg'))

    @respx.mock
    def test_pdf_unauthorized(self):
        respx.get(self.document_url('my-index', 'id-pdf-unauthorized')).mock(return_value=Response(401))
        response = self.client.get('/api/v1/pdf/my-index/id-pdf-unauthorized')
        self.assertEqual(response.status_code, 401)

    @respx.mock
    def test_pdf_root_too_big(self):
        respx.get(self.document_url('my-index', 'rooting-id')).mock(return_value=Response(200, json={'_source': self._root_big_source}))
        respx.get(self.document_url('my-index', 'id-odt-root-too-big')).mock(return_value=Response(200, json={'_source': self._source}))
        response = self.client.get('/api/v1/pdf/my-index/id-odt-root-too-big?routing=rooting-id', headers=auth_headers())
        self.assertEqual(response.status_code, 413)

    @respx.mock
    def test_pdf_timeout(self):
        respx.get(self.document_url('my-index', 'id-odt-timeout')).mock(return_value=Response(200, json={'_source': self._source}))
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-odt-timeout/raw.odt')
        with patch.object(Document, 'get_pdf_preview', side_effect=TimeoutExpired('soffice', 60)):
            response = self.client.get('/api/v1/pdf/my-index/id-odt-timeout', headers=auth_headers())
        self.assertEqual(response.status_code, 415)
        self.assertFalse(os.path.exists('/tmp/documents/my-index/id-odt-timeout'))

    def test_pdf_rejects_routing_with_path_traversal(self):
        response = self.client.get('/api/v1/pdf/my-index/some-id?routing=../../../traversal-target', headers=auth_headers())
        self.assertEqual(response.status_code, 400)
