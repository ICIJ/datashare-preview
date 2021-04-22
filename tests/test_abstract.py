import json
import os
import unittest
import urllib.parse

from concurrent.futures import ThreadPoolExecutor
from dspreview.main import app
from dspreview.config import settings
from fastapi.testclient import TestClient
from http.server import BaseHTTPRequestHandler, HTTPServer
from shutil import copyfile


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
        self.client = TestClient(app)

    def datashare_url(self, path):
        return urllib.parse.urljoin(settings.ds_host, path)
