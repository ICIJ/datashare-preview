import os
import requests

from pathlib import Path
from functools import lru_cache
from tempfile import mktemp
from flask import Flask, send_file, abort, request, jsonify
from flask_cors import CORS
from preview_generator.manager import PreviewManager
from pathlib import Path
from requests.compat import urljoin
from utils import hash_dict

CACHE_PATH = os.environ.get('CACHE_PATH', './cache')
DS_HOST = os.environ.get('DS_HOST', 'http://localhost:8080')
DS_DOCUMENT_PATH = os.environ.get('DS_DOCUMENT_PATH', '/api/index/src/%s/%s')
DS_SESSION_COOKIE_NAME = '_ds_session_id'
DS_SESSION_HEADER_NAME = 'X-Ds-Session-Id'

sizes = dict(xs=80, sm=310, md=540, lg=720, xl=960)

app = Flask(__name__)
CORS(app)

def get_jpeg_preview(params, cache_path = CACHE_PATH):
    manager = PreviewManager(cache_path, create_folder = True)
    return manager.get_jpeg_preview(**params)

def get_size_width(size):
    if str(size).isnumeric():
        return int(size)
    else:
        return sizes.get(size, sizes.get('xs'))

def get_document_url(index, id, routing = None):
    url = urljoin(DS_HOST, DS_DOCUMENT_PATH % (index, id))
    # Optional routing parameter
    if routing is not None: url = urljoin(url, '?routing=%s' % routing)
    return url

def download_document_with_steam(url, cookies):
    target_path = mktemp()
    print(cookies)
    response = requests.get(url, stream=True, cookies=cookies)
    handle = open(target_path, "wb")
    for chunk in response.iter_content(chunk_size=1024):
        if chunk: handle.write(chunk)
    return target_path

@hash_dict
@lru_cache()
def download_document_once(url, cookies):
    return download_document_with_steam(url, cookies)

def download_document(url, cookies):
    target_path = download_document_once(url, cookies)
    # Ensure the file style exist
    if not Path(target_path).exists():
        download_document_once.cache_clear()
        target_path = download_document_once(url, cookies)
    return target_path

def has_session_cookie():
    return DS_SESSION_COOKIE_NAME in request.cookies

def has_session_header():
    return DS_SESSION_HEADER_NAME in request.headers

def get_cookies_from_forwarded_headers():
    cookies = request.cookies.copy()
    # DS_SESSION_COOKIE_NAME is present? Just return the request cookies
    if not has_session_cookie() and has_session_header():
        # Look for DS_SESSION_HEADER_NAME in the request header to build cookies
        cookies = dict()
        cookies[DS_SESSION_COOKIE_NAME] = request.headers.get(DS_SESSION_HEADER_NAME, '')
    return cookies

def get_preview_generator_params(index, id):
    routing = request.args.get('routing', None)
    size = request.args.get('size', 'xs')
    page = request.args.get('page', 0)
    # Build the document URL
    document_url = get_document_url(index, id, routing)
    # Download the document and return the temporary filepath
    file_path = download_document(document_url, get_cookies_from_forwarded_headers())
    return dict(file_path=file_path, height=get_size_width(size), page=int(page))

@app.route('/api/v1/thumbnail/<string:index>/<string:id>', methods=['GET'])
@app.route('/api/v1/thumbnail/<string:index>/<string:id>.jpg', methods=['GET'])
def thumbnail(index, id):
    params = get_preview_generator_params(index, id)
    # The file is not authorized
    if params['file_path'] is None: abort(401)
    # If it not working, PreviewManager will raise an exception
    try: return send_file(get_jpeg_preview(params), as_attachment=False)
    # Silently fail
    except Exception as e: abort(500, e)

@app.route('/api/v1/thumbnail/<string:index>/<string:id>.json', methods=['GET'])
def info(index, id):
    params = get_preview_generator_params(index, id)
    # The file is not authorized
    if params['file_path'] is None: abort(401)
    # If it not working, PreviewManager will raise an exception
    try:
        manager = PreviewManager(CACHE_PATH, create_folder = True)
        return jsonify({
            'pages': manager.get_page_nb(params['file_path']),
            'minetype': manager.get_mimetype(params['file_path']),
            'previewable': manager.has_jpeg_preview(params['file_path'])
        })
    # Silently fail
    except Exception as e: abort(500, e)
