import json
import respx

from httpx import Response
from .test_abstract import auth_headers, create_file_ondisk_from_resource
from .test_abstract import AbstractTest

class SpreadsheetTest(AbstractTest):

    _source = {
        "contentType": "application/vnd.oasis.opendocument.spreadsheet",
        "path": "dummy.ods",
        "contentLength": 123
    }

    @respx.mock
    def test_ods_json(self):
        mocked_url = self.datashare_url('/api/index/search/my-index/_doc/dummy-ods')
        respx.get(mocked_url).mock(return_value=Response(200, json={ "_source": self._source }))
        create_file_ondisk_from_resource('dummy.ods', '/tmp/documents/my-index/dummy-ods/raw.ods')

        response = self.client.get('/api/v1/thumbnail/my-index/dummy-ods.json?include-content=1', headers=auth_headers())
        response_body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response_body['content'], {
            'meals': [['name'], ['couscous'], ['hummus'], ['paella']],
            'people': [['firstname', 'lastname'], ['foo', 'bar']]
        })
        self.assertEqual(response_body['content_type'], 'application/vnd.oasis.opendocument.spreadsheet')
        self.assertEqual(response_body['pages'], 2)
        self.assertEqual(response_body['previewable'], True)
