import os
import requests

from requests.compat import urljoin
from datetime import datetime
from tempfile import gettempdir
from glob import glob
from pathlib import Path
from dspreview.preview import is_content_type_previewable

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())
DS_HOST = os.environ.get('DS_HOST', 'http://localhost:8080')
DS_FILE_PREFIX = os.environ.get('DS_FILE_PREFIX', 'ds-preview-')
DS_DOCUMENT_META_PATH = os.environ.get('DS_DOCUMENT_META_PATH', '/api/index/search/%s/doc/%s')
DS_DOCUMENT_SRC_PATH = os.environ.get('DS_DOCUMENT_SRC_PATH', '/api/%s/documents/src/%s')
DS_DOCUMENT_MAX_SIZE = os.environ.get('DS_DOCUMENT_MAX_SIZE', 50e6) # 50 MB
DS_DOCUMENT_MAX_AGE = os.environ.get('DS_DOCUMENT_MAX_AGE', 60 * 60 * 24 * 3) # 3 days


def build_document_meta_url(index, id, routing = None):
    url = urljoin(DS_HOST, DS_DOCUMENT_META_PATH % (index, id))
    # Optional routing parameter
    if routing is not None: url = urljoin(url, '?_source=contentLength,contentType,path&routing=%s' % routing)
    return url


def build_document_src_url(index, id, routing = None):
    url = urljoin(DS_HOST, DS_DOCUMENT_SRC_PATH % (index, id))
    # Optional routing parameter
    if routing is not None: url = urljoin(url, '?routing=%s' % routing)
    return url


def build_document_target_path(index, id, routing = None):
    file_name = '%s-%s-%s' % (DS_FILE_PREFIX, index, id)
    return os.path.join(CACHE_PATH, file_name)


def get_file_age(file):
    return datetime.now().timestamp() - os.path.getmtime(file)


def is_file_expired(file):
    return get_file_age(file) > int(DS_DOCUMENT_MAX_AGE)


def expired_documents():
    files = glob(os.path.join(CACHE_PATH, '%s*' % DS_FILE_PREFIX))
    return [ file for file in files if is_file_expired(file) ]


def delete_expired_documents():
    for file_path in expired_documents():
        os.remove(file_path)


def download_document_with_steam(url, target_path, cookies):
    response = requests.get(url, stream=True, cookies=cookies)
    with open(target_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
        return target_path


def download_document(index, id, routing, cookies):
    # Build the document URL
    url = build_document_src_url(index, id, routing)
    target_path = build_document_target_path(index, id, routing)
    # Ensure the file style exist
    if not Path(target_path).exists():
        download_document_with_steam(url, target_path, cookies)
    return target_path


def check_user_authorization(index, id, routing, cookies):
    url = build_document_meta_url(index, id, routing)
    response = requests.get(url, cookies=cookies)
    # Raise exception if the document request didn't succeed
    if response.status_code == 401: raise DocumentUnauthorized()
    # Find the content type and content length in nested attributes
    json_response = response.json()
    content_type = json_response.get('_source', {}).get('contentType', None)
    content_length = json_response.get('_source', {}).get('contentLength', 0)
    # Raise exception if the contentType is not previewable
    if not is_content_type_previewable(content_type): raise DocumentNotPreviewable()
    # Raise exception if the contentType is not previewable
    if content_length > DS_DOCUMENT_MAX_SIZE: raise DocumentTooBig()
    return json_response

class DocumentUnauthorized(Exception):
    pass

class DocumentNotPreviewable(Exception):
    pass

class DocumentTooBig(Exception):
    pass
