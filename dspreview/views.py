import logging
from os.path import splitext

import pkg_resources
from pyramid.httpexceptions import exception_response
from pyramid.response import Response, FileResponse
from pyramid.view import view_config

from dspreview.document import Document, DocumentTooBig, DocumentNotPreviewable, DocumentUnauthorized
from dspreview.preview import get_size_width
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


def get_preview_generator_params(request):
    size = request.GET.get('size', 'xs')
    page = request.GET.get('page', 0)
    cookies = get_cookies_from_forwarded_headers(request)
    # Build a document instance
    document = get_request_document(request)
    es_json = document.check_user_authorization(cookies)
    file_path = document.download_document(cookies)
    file_ext = splitext(es_json.get('_source').get('path'))[1]
    return dict(file_path=file_path,
                file_ext=file_ext,
                height=get_size_width(size),
                page=int(page))


def get_request_document(request):
    settings = request.registry.settings
    index = request.matchdict['index']
    id = request.matchdict['id']
    routing = request.GET.get('routing', None)
    return Document(settings, index, id, routing)


@view_config(route_name='home')
def home(_):
    return Response(content_type='text/plain',
                    body='Datashare preview v%s' % pkg_resources.get_distribution("datashare_preview").version)


@view_config(route_name='info_options')
@view_config(route_name='thumbnail_options')
def thumbnail_options(_): return Response()


@view_config(route_name='thumbnail')
def thumbnail(request):
    try:
        params = get_preview_generator_params(request)
        document = get_request_document(request)
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
        params = get_preview_generator_params(request)
        document = get_request_document(request)
        content_type = document.manager.get_mimetype(params['file_path'], params['file_ext'])
        print(content_type, params)
        pages = document.manager.get_page_nb(params['file_path'], '.ods')
        # Disabled content preview if not requested explicitely
        if request.GET.get('include-content'):
            print(params['file_path'], params['file_ext'])
            content = document.get_json_preview(params['file_ext'], content_type)
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
