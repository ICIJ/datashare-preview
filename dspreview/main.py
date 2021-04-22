import logging
import pkg_resources

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from dspreview.cache import DocumentCache
from dspreview.config import settings
from dspreview.document import Document, DocumentTooBig, DocumentNotPreviewable, DocumentUnauthorized
from dspreview.preview import get_size_height
from dspreview.utils import is_truthy
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[settings.ds_session_header_name],
)

def has_session_cookie(request):
    enabled = is_truthy(settings.ds_session_cookie_enabled)
    name = settings.ds_session_cookie_name
    return enabled and name in request.cookies


def has_session_header(request):
    enabled = is_truthy(settings.ds_session_header_enabled)
    name = settings.ds_session_header_name
    return enabled and name in request.headers


def get_cookies_from_forwarded_headers(request):
    if not has_session_cookie(request) and has_session_header(request):
        session_cookie_name = settings.ds_session_cookie_name
        session_header_name = settings.ds_session_header_name
        cookies = dict()
        cookies[session_cookie_name] = request.headers.get(session_header_name, '')
        return cookies
    return request.cookies


def get_preview_generator_params(request, document):
    size = request.query_params.get('size', 'xs')
    page = int(request.query_params.get('page', 0))
    height = get_size_height(size)
    cookies = get_cookies_from_forwarded_headers(request)
    document.download_meta(cookies)
    file_path = document.download_document(cookies)
    file_ext = document.target_ext
    return dict(file_path=file_path, file_ext=file_ext, height=height, page=page)


def get_request_document(request):
    index = request.path_params['index']
    id = request.path_params['id']
    routing = request.query_params.get('routing', None)
    return Document(index, id, routing)


def purge_document_cache():
    max_age = int(settings.ds_document_max_age)
    DocumentCache(max_age).purge()


@app.get("/", response_class=PlainTextResponse)
async def home():
    v = pkg_resources.get_distribution("datashare_preview").version
    return 'Datashare preview v%s' % v


@app.get("/api/v1/thumbnail/{index}/{id}.json")
async def info(request: Request):
    try:
        purge_document_cache()
        document = get_request_document(request)
        params = get_preview_generator_params(request, document)
        content_type = document.manager.get_mimetype(params['file_path'], params['file_ext'])
        pages = document.manager.get_page_nb(params['file_path'], params['file_ext'])
        # Disabled content preview if not requested explicitely
        if request.query_params.get('include-content'):
            content = document.get_json_preview(params, content_type)
        else:
            content = None
        return {
            'content': content,
            'content_type': content_type,
            'pages': pages,
            'previewable': True,
        }
    except DocumentNotPreviewable:
        return { 'pages': 0, 'previewable': False }
    except DocumentTooBig:
        raise HTTPException(status_code=509, detail="Document too big")
    except DocumentUnauthorized:
        raise HTTPException(status_code=401)


@app.get("/api/v1/thumbnail/{index}/{id}")
async def thumbnail(request: Request):
    try:
        document = get_request_document(request)
        params = get_preview_generator_params(request, document)
        return FileResponse(document.get_jpeg_preview(params))
    except DocumentTooBig:
        raise HTTPException(status_code=509, detail="Document too big")
    except DocumentNotPreviewable:
        raise HTTPException(status_code=403, detail="Document not previewable")
    except DocumentUnauthorized:
        raise HTTPException(status_code=401)
