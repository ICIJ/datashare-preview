import respx

from httpx import Response
from .test_abstract import auth_headers, create_file_ondisk_from_resource
from .test_abstract import AbstractTest


class PdfTest(AbstractTest):

    _source = {
        "contentType": "application/vnd.oasis.opendocument.text",
        "path": "dummy.odt",
        "contentLength": 8892
    }

    @respx.mock
    def test_info_json_for_odt(self):
        respx.get(self.document_url('my-index', 'id-for-dummy-odt')).mock(return_value=Response(200, json={'_source': self._source}))
        create_file_ondisk_from_resource('dummy.odt', '/tmp/documents/my-index/id-for-dummy-odt/raw.odt')
        response = self.client.get('/api/v1/thumbnail/my-index/id-for-dummy-odt.json', headers=auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['previewable'])
        self.assertEqual(response.json()['pages'], 1)
