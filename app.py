import os
import requests

from pathlib import Path
from functools import lru_cache
from tempfile import mktemp
from flask import Flask, send_file, abort, request
from preview_generator.manager import PreviewManager
from pathlib import Path
from requests.compat import urljoin

CACHE_PATH = os.environ.get('CACHE_PATH', './cache')
DS_HOST = os.environ.get('DS_HOST', 'http://localhost:8080')
DS_DOCUMENT_PATH = os.environ.get('DS_DOCUMENT_PATH', '/api/index/src/%s/%s')

app = Flask(__name__)
sizes = dict(xs=80, sm=310, md=540, lg=720, xl=960)

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

def download_document_with_steam(url):
    target_path = mktemp()
    response = requests.get(url, stream=True, cookies=request.cookies)
    handle = open(target_path, "wb")
    for chunk in response.iter_content(chunk_size=1024):
        if chunk: handle.write(chunk)
    return target_path

@lru_cache()
def download_document_once(url):
    return download_document_with_steam(url)

def download_document(url):
    target_path = download_document_once(url)
    # Ensure the file style exist
    if not Path(target_path).exists():
        download_document_once.cache_clear()
        target_path = download_document_once(url)
    return target_path

def get_preview_generator_params(index, id):
    routing = request.args.get('routing', None)
    size = request.args.get('size', 'xs')
    page = request.args.get('page', 0)
    # Build the document URL
    document_url = get_document_url(index, id, routing)
    # Download the document and return the temporary filepath
    file_path = download_document(document_url)
    return dict(file_path=file_path, width=get_size_width(size), page=int(page))

@app.route('/api/v1/thumbnail/<string:index>/<string:id>', methods=['GET'])
def preview(index, id):
    params = get_preview_generator_params(index, id)
    # The file is not authorized
    if params['file_path'] is None: abort(401)
    # If it not working, PreviewManager will raise an exception
    try: return send_file(get_jpeg_preview(params), as_attachment=False)
    # Silently fail
    except Exception as e: abort(500, e)
