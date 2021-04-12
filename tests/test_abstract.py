import json
import os
import unittest
import urllib.parse

from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from shutil import copyfile
from dspreview import main
from webtest import TestApp


def create_file_ondisk_from_resource(resource_name, path):
    target_directory = os.path.dirname(path)
    current_directory = os.path.dirname(os.path.realpath(__file__))
    resource_path = os.path.join(current_directory, 'resources', resource_name)
    os.makedirs(target_directory, exist_ok = True)
    copyfile(resource_path, path)


def auth_headers():
    return {'Cookie': '_ds_session_id={"login":"userid","roles":[],"sessionId":"sid","redirectAfterLogin":"/"}'}


class AbstractTest(unittest.TestCase):

    def setUp(self):
        self.settings = {
            'ds.host': 'http://localhost:8080',
            'ds.document.meta.path': '/api/index/search/%s/_doc/%s',
            'ds.document.src.path': '/api/%s/documents/src/%s',
            'ds.document.max.size': '50000000',
            'ds.document.max.age': '259200',
            'ds.session.cookie.enabled': 'true',
            'ds.session.cookie.name': '_ds_session_id',
            'ds.session.header.enabled': 'true',
            'ds.session.header.name': 'X-Ds-Session-Id',
        }
        app = main({}, **self.settings)
        self.app = TestApp(app)

    def datashare_url(self, path):
        return urllib.parse.urljoin(self.settings['ds.host'], path)

    def assert_cors_headers_ok(self, response):
        self.assertEqual('*', response.headers.get('Access-Control-Allow-Origin'))
        self.assertEqual('GET', response.headers.get('Access-Control-Allow-Methods'))
        self.assertEqual('x-ds-session-id', response.headers.get('Access-Control-Allow-Headers'))
