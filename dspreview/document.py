import os
import requests

from requests.compat import urljoin
from datetime import datetime
from pathlib import Path
from dspreview.cache import THUMBNAILS_PATH, DOCUMENTS_PATH
from dspreview.config import settings
from dspreview.spreadsheet import is_content_type_spreadsheet, is_ext_spreadsheet, get_spreadsheet_preview
from preview_generator.manager import PreviewManager

class Document:
    def __init__(self, index, id, routing):
        self.index = index
        self.id = id
        self.routing = routing
        self.source = {}
        self.setup_target_directory()
        self.manager = PreviewManager(self.thumbnail_directory, create_folder = True)


    @property
    def meta_url(self):
        url = urljoin(settings.ds_host, settings.ds_document_meta_path % (self.index, self.id))
        # Optional routing parameter
        if self.routing is not None:
            url = urljoin(url, '?_source=contentLength,contentType,path&routing=%s' % self.routing)
        return url


    @property
    def src_url(self):
        url = urljoin(settings.ds_host, settings.ds_document_src_path % (self.index, self.id))
        # Optional routing parameter
        if self.routing is not None:
            url = urljoin(url, '?routing=%s' % self.routing)
        return url


    @property
    def target_path(self):
        if self.target_ext is None:
            return os.path.join(self.target_directory, 'raw')
        else:
            return os.path.join(self.target_directory, 'raw' + self.target_ext)


    @property
    def target_directory(self):
        return os.path.join(DOCUMENTS_PATH, self.index, self.id)


    @property
    def target_ext(self):
        if self.target_path_ext == '':
            if self.target_content_type is None:
                return None
            return self.manager.get_file_extension()
        return self.target_path_ext


    @property
    def target_path_ext(self):
        return Path(self.source.get('path', '')).suffix

    @property
    def target_content_type(self):
        return self.source.get('contentType', None)


    @property
    def thumbnail_directory(self):
        return os.path.join(THUMBNAILS_PATH, self.index, self.id)


    def setup_target_directory(self):
        return os.makedirs(self.target_directory, exist_ok = True)


    def download_document_with_steam(self, cookies):
        # Download meta if none
        if not self.source: self.download_meta(cookies)
        # Open a stream on the document URL
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


    def download_meta(self, cookies):
        response = requests.get(self.meta_url, cookies=cookies)
        # Raise exception if the document request didn't succeed
        if response.status_code == 401:
            raise DocumentUnauthorized()
        # Any other error
        elif not response.ok:
            raise DocumentNotPreviewable()
        # Save the source meta
        self.source = response.json().get('_source', {})


    def check_user_authorization(self, cookies):
        # Download meta if none
        if not self.source: self.download_meta(cookies)
        # Read contentType and contentLength from source
        content_type = self.source.get('contentType', None)
        content_length = self.source.get('contentLength', 0)
        # Raise exception if the contentType is not previewable
        if not self.is_content_type_previewable(content_type):
            raise DocumentNotPreviewable()
        # Raise exception if the contentType is not previewable
        if content_length > int(settings.ds_document_max_size):
            raise DocumentTooBig()


    def get_jpeg_preview(self, params):
        return self.manager.get_jpeg_preview(**params)


    def get_json_preview(self, params, content_type):
        # Only spreadsheet preview is supported yet
        if is_content_type_spreadsheet(content_type) or is_ext_spreadsheet(params['file_ext']):
            return get_spreadsheet_preview(params)
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
