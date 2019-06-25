import os

from flask import Flask, send_file, abort, request, jsonify
from flask_cors import CORS
from preview import get_jpeg_preview, get_size_width, is_content_type_previewable, build_preview_manager
from document import delete_expired_documents, download_document, build_document_meta_url, check_user_authorization
from document import DocumentUnauthorized, DocumentNotPreviewable, DocumentTooBig

DS_SESSION_COOKIE_NAME = '_ds_session_id'
DS_SESSION_HEADER_NAME = 'X-Ds-Session-Id'

app = Flask(__name__)
CORS(app)

def has_session_cookie():
    return DS_SESSION_COOKIE_NAME in request.cookies

def has_session_header():
    return DS_SESSION_HEADER_NAME in request.headers

def get_cookies_from_forwarded_headers(request):
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
    cookies = get_cookies_from_forwarded_headers(request)
    # Some files might had expired
    delete_expired_documents()
    # Beck the user can access the doucment
    check_user_authorization(index, id, routing, cookies)
    # Download the document and return the temporary filepath
    file_path = download_document(index, id, routing, cookies)
    return dict(file_path=file_path, height=get_size_width(size), page=int(page))

@app.route('/api/v1/thumbnail/<string:index>/<string:id>', methods=['GET'])
@app.route('/api/v1/thumbnail/<string:index>/<string:id>.jpg', methods=['GET'])
def thumbnail(index, id):
    try:
        params = get_preview_generator_params(index, id)
        return send_file(get_jpeg_preview(params), as_attachment=False)
    except DocumentTooBig: abort(509)
    except DocumentNotPreviewable: abort(403)
    except DocumentUnauthorized: abort(401)
    except Exception: abort(500)

@app.route('/api/v1/thumbnail/<string:index>/<string:id>.json', methods=['GET'])
def info(index, id):
    manager = build_preview_manager()
    try:
        params = get_preview_generator_params(index, id)
        pages = manager.get_page_nb(params['file_path'])
        return jsonify({ 'pages': pages, 'previewable': True })
    except DocumentNotPreviewable:
        return jsonify({ 'pages': 0, 'previewable': False })
    except DocumentTooBig: abort(509)
    except DocumentUnauthorized: abort(401)
    except Exception: abort(500)
