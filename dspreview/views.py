import logging

import pkg_resources
from pyramid.httpexceptions import exception_response
from pyramid.response import Response, FileResponse
from pyramid.view import view_config

from dspreview.document import Document, DocumentTooBig, DocumentNotPreviewable, DocumentUnauthorized
from dspreview.preview import get_size_height
from dspreview.utils import is_truthy

log = logging.getLogger(__name__)

def has_session_cookie(request):
    enabled = is_truthy(request.registry.settings.get('ds.session.cookie.enabled'))
    name = request.registry.settings['ds.session.cookie.name']
    return enabled and name in request.cookies


def has_session_header(request):
    enabled = is_truthy(request.registry.settings.get('ds.session.header.enabled'))
    name = request.registry.settings['ds.session.header.name']
    return enabled and name in request.headers


def get_cookies_from_forwarded_headers(request):
    if not has_session_cookie(request) and has_session_header(request):
        session_cookie_name = request.registry.settings['ds.session.cookie.name']
        session_header_name = request.registry.settings['ds.session.header.name']
        cookies = dict()
        cookies[session_cookie_name] = request.headers.get(session_header_name, '')
        return cookies
    return request.cookies


def get_preview_generator_params(request, document):
    size = request.GET.get('size', 'xs')
    page = int(request.GET.get('page', 0))
    height = get_size_height(size)
    cookies = get_cookies_from_forwarded_headers(request)
    document.download_meta(cookies)
    file_path = document.download_document(cookies)
    file_ext = document.target_ext
    return dict(file_path=file_path, file_ext=file_ext, height=height, page=page)


def get_request_document(request):
    settings = request.registry.settings
    index = request.matchdict['index']
    id = request.matchdict['id']
    routing = request.GET.get('routing', None)
    return Document(settings, index, id, routing)


@view_config(route_name='home')
def home(_):
    v = pkg_resources.get_distribution("datashare_preview").version
    return Response(content_type='text/plain', body='Datashare preview v%s' % v)


@view_config(route_name='info_options')
@view_config(route_name='thumbnail_options')
def thumbnail_options(_):
    return Response()


@view_config(route_name='thumbnail')
def thumbnail(request):
    try:
        document = get_request_document(request)
        params = get_preview_generator_params(request, document)
        return FileResponse(document.get_jpeg_preview(params), content_type='image/jpeg')
    except DocumentTooBig:
        raise exception_response(509)
    except DocumentNotPreviewable:
        raise exception_response(403)
    except DocumentUnauthorized:
        raise exception_response(401)


@view_config(route_name='info', renderer='json')
def info(request):
    try:
        document = get_request_document(request)
        params = get_preview_generator_params(request, document)
        content_type = document.manager.get_mimetype(params['file_path'], params['file_ext'])
        pages = document.manager.get_page_nb(params['file_path'], params['file_ext'])
        # Disabled content preview if not requested explicitely
        if request.GET.get('include-content'):
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
        raise exception_response(509)
    except DocumentUnauthorized:
        raise exception_response(401)
