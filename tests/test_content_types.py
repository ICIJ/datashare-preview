import respx

from glob import glob
from shutil import rmtree
from unittest.mock import patch

from httpx import Response
from dspreview import video
from dspreview.document import Document
from .test_abstract import auth_headers, create_file_ondisk_from_resource
from .test_abstract import AbstractTest

DOCUMENT_CONTENT_TYPES = {
  'application/msword': 'dummy.doc',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'dummy.docx',
  'application/vnd.oasis.opendocument.text': 'dummy.odt',
  'application/rtf': 'dummy.rtf',
  'application/vnd.ms-powerpoint': 'dummy.ppt',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'dummy.pptx',
  'application/vnd.oasis.opendocument.presentation': 'dummy.odp',
  'image/vnd.microsoft.icon': 'dummy.ico',
  'image/x-portable-anymap': 'dummy.pnm',
  'image/x-portable-graymap': 'dummy.pgm',
  'image/x-portable-bitmap': 'dummy.pbm',
  'image/x-xbitmap': 'dummy.xbm',
}

SPREADSHEET_CONTENT_TYPES = {
  'application/vnd.ms-excel.sheet.macroenabled.12': 'dummy.xlsm',
  'application/vnd.oasis.opendocument.spreadsheet-template': 'dummy.ots',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.template': 'dummy.xltx',
}

VIDEO_CONTENT_TYPES = {
  'video/quicktime': 'dummy.mov',
  'video/mp4': 'dummy.mp4',
}


class ContentTypesTest(AbstractTest):

    def mock_document(self, resource_name, content_type):
        document_id = f'{content_type}-{resource_name}'.replace('/', '-').replace('.', '-')
        source = {'contentType': content_type, 'path': resource_name, 'contentLength': 123}
        mocked_url = self.document_url('my-index', document_id)
        respx.get(mocked_url).mock(return_value=Response(200, json={'_source': source}))
        extension = resource_name.split('.')[-1]
        create_file_ondisk_from_resource(resource_name, f'/tmp/documents/my-index/{document_id}/raw.{extension}')
        thumbnail_directory = Document('my-index', document_id).thumbnail_directory
        rmtree(thumbnail_directory, ignore_errors=True)
        return document_id

    @respx.mock
    def test_thumbnail(self):
        all_content_types = {**DOCUMENT_CONTENT_TYPES, **SPREADSHEET_CONTENT_TYPES, **VIDEO_CONTENT_TYPES}
        for content_type, resource_name in all_content_types.items():
            with self.subTest(content_type=content_type):
                document_id = self.mock_document(resource_name, content_type)
                response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}', headers=auth_headers())
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers['Content-Type'], 'image/jpeg')

    @respx.mock
    def test_spreadsheet_content(self):
        for content_type, resource_name in SPREADSHEET_CONTENT_TYPES.items():
            with self.subTest(content_type=content_type):
                document_id = self.mock_document(resource_name, content_type)
                response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}.json?include-content=1', headers=auth_headers())
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json().get('content'))

    @respx.mock
    def test_video_info_has_one_page(self):
        for content_type, resource_name in VIDEO_CONTENT_TYPES.items():
            with self.subTest(content_type=content_type):
                document_id = self.mock_document(resource_name, content_type)
                response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}.json', headers=auth_headers())
                self.assertEqual(response.json().get('previewable'), True)
                self.assertEqual(response.json().get('pages'), 1)

    @respx.mock
    def test_video_thumbnail_any_page_is_poster_frame(self):
        document_id = self.mock_document('dummy.mov', 'video/quicktime')
        first = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}?page=0', headers=auth_headers())
        other = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}?page=3', headers=auth_headers())
        self.assertEqual(other.status_code, 200)
        self.assertEqual(other.content, first.content)

    @respx.mock
    def test_video_thumbnail_any_page_reuses_poster_frame(self):
        document_id = self.mock_document('dummy.mov', 'video/quicktime')
        self.client.get(f'/api/v1/thumbnail/my-index/{document_id}?page=0', headers=auth_headers())
        self.client.get(f'/api/v1/thumbnail/my-index/{document_id}?page=3', headers=auth_headers())
        thumbnail_directory = Document('my-index', document_id).thumbnail_directory
        thumbnails = glob(f'{thumbnail_directory}/*.jpeg')
        self.assertEqual(len(thumbnails), 1)

    @respx.mock
    def test_video_info_not_previewable(self):
        resource_names = ['dummy-audio-only.mov', 'dummy-corrupt.mov']
        for resource_name in resource_names:
            with self.subTest(resource_name=resource_name):
                document_id = self.mock_document(resource_name, 'video/quicktime')
                response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}.json', headers=auth_headers())
                self.assertEqual(response.json().get('previewable'), False)

    @respx.mock
    def test_video_thumbnail_without_duration(self):
        real_probe = video.probe
        def probe_without_duration(file_path):
            probe_data = real_probe(file_path)
            del probe_data['format']['duration']
            return probe_data
        document_id = self.mock_document('dummy.mov', 'video/quicktime')
        with patch('dspreview.video.probe', probe_without_duration):
            response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}', headers=auth_headers())
        self.assertEqual(response.status_code, 200)

    @respx.mock
    def test_video_thumbnail_timeout(self):
        document_id = self.mock_document('dummy.mov', 'video/quicktime')
        with patch('dspreview.video.TIMEOUT_SECONDS', 0.001):
            response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}', headers=auth_headers())
        self.assertEqual(response.status_code, 415)

    @respx.mock
    def test_video_thumbnail_not_previewable(self):
        resource_names = ['dummy-audio-only.mov', 'dummy-corrupt.mov']
        for resource_name in resource_names:
            with self.subTest(resource_name=resource_name):
                document_id = self.mock_document(resource_name, 'video/quicktime')
                response = self.client.get(f'/api/v1/thumbnail/my-index/{document_id}', headers=auth_headers())
                self.assertEqual(response.status_code, 415)
