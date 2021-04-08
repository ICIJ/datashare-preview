import os
import requests

from requests.compat import urljoin
from datetime import datetime
from tempfile import gettempdir
from glob import glob
from pathlib import Path
from shutil import rmtree
from dspreview.preview import THUMBNAILS_PATH
from dspreview.spreadsheet import is_content_type_spreadsheet, is_ext_spreadsheet, get_spreadsheet_preview
from preview_generator.manager import PreviewManager

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())
DOCUMENTS_PATH = os.path.join(CACHE_PATH, 'documents')

class Document:
    def __init__(self, settings, index, id, routing):
        self.settings = settings
        self.index = index
        self.id = id
        self.routing = routing
        self.delete_expired_documents()
        self.setup_target_directory()
        self.manager = PreviewManager(self.thumbnail_directory, create_folder = True)


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
        return os.path.join(DOCUMENTS_PATH, self.index, self.id, 'raw')


    @property
    def target_directory(self):
        return os.path.join(DOCUMENTS_PATH, self.index, self.id)


    @property
    def thumbnail_directory(self):
        return os.path.join(THUMBNAILS_PATH, self.index, self.id)


    @property
    def expired_documents(self):
        documents = glob(os.path.join(CACHE_PATH, 'documents/*/*'))
        thumbnails = glob(os.path.join(CACHE_PATH, 'thumbnails/*/*'))
        directories = documents + thumbnails
        return [ dir for dir in directories if self.is_directory_expired(dir) ]


    def setup_target_directory(self):
        return os.makedirs(self.target_directory, exist_ok = True)


    def delete_expired_documents(self):
        for document_directory in self.expired_documents:
            rmtree(document_directory)


    def get_directory_age(self, directory):
        return datetime.now().timestamp() - os.path.getmtime(directory)


    def is_directory_expired(self, directory):
        max_age = int(self.settings['ds.document.max.age'])
        return self.get_directory_age(directory) > max_age


    def download_document_with_steam(self, cookies):
        response = requests.get(self.src_url, stream=True, cookies=cookies)
        with open(self.target_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
            return self.target_path


    def download_document(self, cookies):
        # Ensure the file style doesn't exist
        if not Path(self.target_path).exists():
            # Build the document URL
            self.download_document_with_steam(cookies)
        return self.target_path


    def check_user_authorization(self, cookies):
        response = requests.get(self.meta_url, cookies=cookies)
        # Raise exception if the document request didn't succeed
        if response.status_code == 401: raise DocumentUnauthorized()
        # Any other error
        elif not response.ok:
            raise DocumentNotPreviewable()
        # Find the content type and content length in nested attributes
        json_response = response.json()
        content_type = json_response.get('_source', {}).get('contentType', None)
        content_length = json_response.get('_source', {}).get('contentLength', 0)
        # Raise exception if the contentType is not previewable
        if not self.is_content_type_previewable(content_type): raise DocumentNotPreviewable()
        # Raise exception if the contentType is not previewable
        if content_length > int(self.settings['ds.document.max.size']): raise DocumentTooBig()
        return json_response


    def get_jpeg_preview(self, params):
        return self.manager.get_jpeg_preview(**params)


    def get_json_preview(self, params, content_type):
        file_ext = params['file_ext']
        file_path = params['file_path']
        # Only spreadsheet preview is supported yet
        if self.is_content_type_spreadsheet(content_type) or self.is_ext_spreadsheet(file_ext):
            return self.get_spreadsheet_preview(params)
        else:
            return None


    def is_content_type_previewable(self, content_type):
        return content_type in self.manager.get_supported_mimetypes()


class DocumentUnauthorized(Exception):
    pass

class DocumentNotPreviewable(Exception):
    pass

class DocumentTooBig(Exception):
    pass
