import os
import respx

from shutil import rmtree
from subprocess import TimeoutExpired
from unittest.mock import patch

from httpx import Response
from preview_generator.manager import PreviewManager
from dspreview.cache import DOCUMENTS_PATH
from dspreview.document import Document
from .test_abstract import auth_headers, create_file_ondisk_from_resource, read_resource
from .test_abstract import AbstractTest

PPTM_CONTENT_TYPE = 'application/vnd.ms-powerpoint.presentation.macroenabled.12'


class PdfTest(AbstractTest):

    _source = {
        "contentType": "application/vnd.oasis.opendocument.text",
        "path": "dummy.odt",
        "contentLength": 9046
    }

    _root_big_source = {
        "contentType": "application/pdf",
        "path": "dummy.pdf",
        "contentLength": 60000000
    }

    _session = 'sid'

    def mock_meta(self, id, source):
        mocked_url = self.document_url('my-index', id)
        mocked_response = Response(200, json={'_source': source})
        respx.get(mocked_url).mock(return_value=mocked_response)

    def mock_odt(self, id):
        cookies = {'_ds_session_id': self._session}
        meta_url = self.document_url('my-index', id)
        meta_response = Response(200, json={'_source': self._source})
        respx.get(meta_url, cookies=cookies).mock(return_value=meta_response)
        src_url = self.datashare_url(f'/api/my-index/documents/src/{id}')
        odt_content = read_resource('dummy.odt')
        src_response = Response(200, content=odt_content)
        respx.get(src_url, cookies=cookies).mock(return_value=src_response)
        rmtree(f'/tmp/documents/my-index/{id}', ignore_errors=True)

    def create_truncated_odt(self, id):
        target_directory = f'/tmp/documents/my-index/{id}'
        rmtree(target_directory, ignore_errors=True)
        os.makedirs(target_directory)
        odt_content = read_resource('dummy.odt')
        truncated_odt = odt_content[:3000]
        with open(f'{target_directory}/raw.odt', 'wb') as file:
            file.write(truncated_odt)

    def create_document(self, id, source):
        document = Document('my-index', id)
        document.source = source
        return document

    @respx.mock
    def test_info_json_for_odt(self):
        self.mock_meta('id-for-dummy-odt', self._source)
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-for-dummy-odt/raw.odt')
        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-odt.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['previewable'])
        self.assertEqual(response.json()['pages'], 1)

    @respx.mock
    def test_pdf_for_odt(self):
        self.mock_odt('id-odt-to-pdf')
        headers = {'Cookie': f'_ds_session_id={self._session}'}
        response = self.client.get('/api/v1/pdf/my-index/id-odt-to-pdf', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    @respx.mock
    def test_pdf_with_session_header(self):
        self.mock_odt('id-odt-to-pdf-with-header')
        headers = {'X-Ds-Session-Id': self._session}
        response = self.client.get('/api/v1/pdf/my-index/id-odt-to-pdf-with-header', headers=headers)
        self.assertEqual(response.status_code, 200)

    @respx.mock
    def test_pdf_rejects_jpeg_and_keeps_cache(self):
        jpeg_source = {"contentType": "image/jpeg", "path": "dummy.jpg", "contentLength": 123}
        self.mock_meta('id-jpg-on-pdf', jpeg_source)
        create_file_ondisk_from_resource('dummy.jpg', '/tmp/documents/my-index/id-jpg-on-pdf/raw.jpg')
        response = self.client.get('/api/v1/pdf/my-index/id-jpg-on-pdf', headers=auth_headers())
        self.assertEqual(response.status_code, 415)
        self.assertTrue(os.path.exists('/tmp/documents/my-index/id-jpg-on-pdf/raw.jpg'))

    @respx.mock
    def test_pdf_unauthorized(self):
        mocked_url = self.document_url('my-index', 'id-pdf-unauthorized')
        respx.get(mocked_url).mock(return_value=Response(401))
        response = self.client.get('/api/v1/pdf/my-index/id-pdf-unauthorized')
        self.assertEqual(response.status_code, 401)

    @respx.mock
    def test_pdf_root_too_big(self):
        self.mock_meta('rooting-id', self._root_big_source)
        self.mock_meta('id-odt-root-too-big', self._source)
        response = self.client.get('/api/v1/pdf/my-index/id-odt-root-too-big?routing=rooting-id', headers=auth_headers())
        self.assertEqual(response.status_code, 413)

    @respx.mock
    def test_pdf_timeout(self):
        self.mock_meta('id-odt-timeout', self._source)
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-odt-timeout/raw.odt')
        timeout = TimeoutExpired('soffice', 60)
        with patch.object(Document, 'get_pdf_preview', side_effect=timeout):
            response = self.client.get('/api/v1/pdf/my-index/id-odt-timeout', headers=auth_headers())
        self.assertEqual(response.status_code, 415)
        self.assertFalse(os.path.exists('/tmp/documents/my-index/id-odt-timeout'))

    def test_pdf_rejects_routing_with_path_traversal(self):
        response = self.client.get('/api/v1/pdf/my-index/some-id?routing=../../../traversal-target', headers=auth_headers())
        self.assertEqual(response.status_code, 400)

    @respx.mock
    def test_info_json_for_corrupt_odt(self):
        self.mock_meta('id-corrupt-odt-info', self._source)
        self.create_truncated_odt('id-corrupt-odt-info')
        response = self.client.get('/api/v1/thumbnail/my-index/id-corrupt-odt-info.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['previewable'])

    @respx.mock
    def test_pdf_for_corrupt_odt(self):
        self.mock_meta('id-corrupt-odt-pdf', self._source)
        self.create_truncated_odt('id-corrupt-odt-pdf')
        response = self.client.get('/api/v1/pdf/my-index/id-corrupt-odt-pdf', headers=auth_headers())
        self.assertEqual(response.status_code, 415)

    @respx.mock
    def test_thumbnail_for_corrupt_odt(self):
        self.mock_meta('id-corrupt-odt-thumbnail', self._source)
        self.create_truncated_odt('id-corrupt-odt-thumbnail')
        response = self.client.get('/api/v1/thumbnail/my-index/id-corrupt-odt-thumbnail', headers=auth_headers())
        self.assertEqual(response.status_code, 415)

    @respx.mock
    def test_thumbnail_timeout(self):
        self.mock_meta('id-odt-thumbnail-timeout', self._source)
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-odt-thumbnail-timeout/raw.odt')
        timeout = TimeoutExpired('soffice', 60)
        with patch.object(Document, 'get_jpeg_preview', side_effect=timeout):
            response = self.client.get('/api/v1/thumbnail/my-index/id-odt-thumbnail-timeout', headers=auth_headers())
        self.assertEqual(response.status_code, 415)
        self.assertFalse(os.path.exists('/tmp/documents/my-index/id-odt-thumbnail-timeout'))

    @respx.mock
    def test_pdf_surfaces_missing_libreoffice(self):
        self.mock_meta('id-odt-no-libreoffice', self._source)
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-odt-no-libreoffice/raw.odt')
        missing_binary = FileNotFoundError(2, 'No such file or directory', 'libreoffice')
        with patch.object(PreviewManager, 'get_pdf_preview', side_effect=missing_binary):
            with self.assertRaises(FileNotFoundError):
                self.client.get('/api/v1/pdf/my-index/id-odt-no-libreoffice', headers=auth_headers())
        self.assertTrue(os.path.exists('/tmp/documents/my-index/id-odt-no-libreoffice/raw.odt'))

    def test_target_path_for_pptm_without_extension(self):
        source = {'contentType': PPTM_CONTENT_TYPE, 'path': 'attachment'}
        document = self.create_document('id-pptm-without-extension', source)
        expected_path = os.path.join(DOCUMENTS_PATH, 'my-index', 'id-pptm-without-extension', 'raw')
        self.assertEqual(document.target_path, expected_path)

    def test_pptm_is_previewable(self):
        source = {'contentType': PPTM_CONTENT_TYPE}
        document = self.create_document('id-pptm-previewable', source)
        self.assertFalse(document.is_content_type_not_previewable)

    def test_pptm_is_pdf_convertible(self):
        source = {'contentType': PPTM_CONTENT_TYPE}
        document = self.create_document('id-pptm-convertible', source)
        self.assertTrue(document.is_content_type_pdf_convertible)
