import logging
from os.path import splitext

import pkg_resources
from pyramid.httpexceptions import exception_response
from pyramid.response import Response, FileResponse
from pyramid.view import view_config

from dspreview.document import DocumentTooBig, DocumentNotPreviewable, DocumentUnauthorized, delete_expired_documents, \
    check_user_authorization, download_document
from dspreview.preview import get_jpeg_preview, get_json_preview, build_preview_manager, get_size_width

log = logging.getLogger(__name__)

DS_SESSION_COOKIE_NAME = '_ds_session_id'
DS_SESSION_HEADER_NAME = 'X-Ds-Session-Id'


def has_session_cookie(request):
    return DS_SESSION_COOKIE_NAME in request.cookies


def has_session_header(request):
    return DS_SESSION_HEADER_NAME in request.headers


def get_cookies_from_forwarded_headers(request):
    if not has_session_cookie(request) and has_session_header(request):
        cookies = dict()
        cookies[DS_SESSION_COOKIE_NAME] = request.headers.get(DS_SESSION_HEADER_NAME, '')
        return cookies
    return request.cookies


def get_preview_generator_params(request):
    routing = request.GET.get('routing', None)
    size = request.GET.get('size', 'xs')
    page = request.GET.get('page', 0)
    cookies = get_cookies_from_forwarded_headers(request)
    delete_expired_documents()
    es_json = check_user_authorization(request.matchdict['index'], request.matchdict['id'], routing, cookies)
    file_path = download_document(request.matchdict['index'], request.matchdict['id'], routing, cookies)
    return dict(file_path=file_path, height=get_size_width(size), page=int(page), file_ext=splitext(es_json.get('_source').get('path'))[1])


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
        return FileResponse(get_jpeg_preview(params), content_type='image/jpeg')
    except DocumentTooBig:
        raise exception_response(509)
    except DocumentNotPreviewable:
        raise exception_response(403)
    except DocumentUnauthorized:
        raise exception_response(401)


@view_config(route_name='info', renderer='json')
def info(request):
    manager = build_preview_manager()
    try:
        params = get_preview_generator_params(request)
        pages = manager.get_page_nb(params['file_path'], params['file_ext'])
        content_type = manager.get_mimetype(params['file_path'], params['file_ext'])
        # Disabled content preview if not requested explicitely
        content = get_json_preview(params, content_type) if request.GET.get('include-content') else None
        return {'pages': pages, 'previewable': True, 'content': content, 'content_type': content_type}
    except DocumentNotPreviewable:
        return {'pages': 0, 'previewable': False}
    except DocumentTooBig:
        raise exception_response(509)
    except DocumentUnauthorized:
        raise exception_response(401)
