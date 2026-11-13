import respx

from httpx import Response
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


class ContentTypesTest(AbstractTest):

    def mock_document(self, resource_name, content_type):
        document_id = content_type.replace('/', '-').replace('.', '-')
        source = {'contentType': content_type, 'path': resource_name, 'contentLength': 123}
        mocked_url = self.document_url('my-index', document_id)
        respx.get(mocked_url).mock(return_value=Response(200, json={'_source': source}))
        extension = resource_name.split('.')[-1]
        create_file_ondisk_from_resource(resource_name, f'/tmp/documents/my-index/{document_id}/raw.{extension}')
        return document_id

    @respx.mock
    def test_thumbnail(self):
        all_content_types = {**DOCUMENT_CONTENT_TYPES, **SPREADSHEET_CONTENT_TYPES}
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
