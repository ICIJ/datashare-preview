import os
import requests

from requests.compat import urljoin
from datetime import datetime
from tempfile import gettempdir
from glob import glob
from pathlib import Path
from dspreview.preview import is_content_type_previewable

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())

class Document:
    def __init__(self, settings, index, id, routing):
        self.settings = settings
        self.index = index
        self.id = id
        self.routing = routing


    @property
    def meta_url(self):
        url = urljoin(self.settings['ds.host'], self.settings['ds.document.meta.path'] % (self.index, self.id))
        # Optional routing parameter
        if self.routing is not None:
            url = urljoin(url, '?_source=contentLength,contentType,path&routing=%s' % self.routing)
        return url


    @property
    def src_url(self):
        url = urljoin(self.settings['ds.host'], self.settings['ds.document.src.path'] % (self.index, self.id))
        # Optional routing parameter
        if self.routing is not None:
            url = urljoin(url, '?routing=%s' % self.routing)
        return url


    @property
    def target_path(self):
        file_name = '%s-%s-%s' % (self.settings['ds.file.prefix'], self.index, self.id)
        return os.path.join(CACHE_PATH, file_name)


    @property
    def expired_documents(self):
        files = glob(os.path.join(CACHE_PATH, '%s*' % self.settings['ds.file.prefix']))
        return [ file for file in files if self.is_file_expired(file) ]


    def delete_expired_documents(self):
        for file_path in self.expired_documents:
            os.remove(file_path)


    def get_file_age(self, file):
        return datetime.now().timestamp() - os.path.getmtime(file)


    def is_file_expired(self, file):
        return self.get_file_age(file) > int(self.settings['ds.document.max.age'])


    def download_document_with_steam(self, cookies):
        response = requests.get(self.src_url, stream=True, cookies=cookies)
        with open(self.target_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
            return self.target_path


    def download_document(self, cookies):
        # Ensure the file style exist
        if not Path(self.target_path).exists():
            # Build the document URL
            self.download_document_with_steam(cookies)
        return self.target_path


    def check_user_authorization(self, cookies):
        response = requests.get(self.meta_url, cookies=cookies)
        # Raise exception if the document request didn't succeed
        if response.status_code == 401: raise DocumentUnauthorized()
        # Find the content type and content length in nested attributes
        json_response = response.json()
        content_type = json_response.get('_source', {}).get('contentType', None)
        content_length = json_response.get('_source', {}).get('contentLength', 0)
        # Raise exception if the contentType is not previewable
        if not is_content_type_previewable(content_type): raise DocumentNotPreviewable()
        # Raise exception if the contentType is not previewable
        if content_length > int(self.settings['ds.document.max.size']): raise DocumentTooBig()
        return json_response


class DocumentUnauthorized(Exception):
    pass

class DocumentNotPreviewable(Exception):
    pass

class DocumentTooBig(Exception):
    pass
