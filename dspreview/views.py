import pkg_resources
from pyramid.httpexceptions import exception_response
from pyramid.response import Response
from pyramid.view import view_config

from dspreview.document import DocumentTooBig, DocumentNotPreviewable, DocumentUnauthorized, delete_expired_documents, \
    check_user_authorization, download_document
from dspreview.preview import get_jpeg_preview, build_preview_manager, get_size_width

DS_SESSION_COOKIE_NAME = '_ds_session_id'
DS_SESSION_HEADER_NAME = 'X-Ds-Session-Id'


def has_session_cookie(request):
    return DS_SESSION_COOKIE_NAME in request.cookies


def has_session_header(request):
    return DS_SESSION_HEADER_NAME in request.headers


def get_cookies_from_forwarded_headers(request):
    cookies = request.cookies.copy()
    if not has_session_cookie(request) and has_session_header(request):
        cookies = dict()
        cookies[DS_SESSION_COOKIE_NAME] = request.headers.get(DS_SESSION_HEADER_NAME, '')
    return cookies


def get_preview_generator_params(request):
    routing = request.args.get('routing', None)
    size = request.args.get('size', 'xs')
    page = request.args.get('page', 0)
    cookies = get_cookies_from_forwarded_headers(request)
    delete_expired_documents()
    check_user_authorization(request.matchdict['index'], request.matchdict['id'], routing, cookies)
    file_path = download_document(request.matchdict['index'], request.matchdict['id'], routing, cookies)
    return dict(file_path=file_path, height=get_size_width(size), page=int(page))


@view_config(route_name='home')
def home(_):
    return Response(content_type='text/plain',
                    body='Datashare preview v%s' % pkg_resources.get_distribution("datashare_preview").version)


@view_config(route_name='thumbnail')
def thumbnail(request):
    try:
        params = get_preview_generator_params(request)
        return Response(content_type='image/jpeg', body=get_jpeg_preview(params))
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
        pages = manager.get_page_nb(params['file_path'])
        return {'pages': pages, 'previewable': True}
    except DocumentNotPreviewable:
        return {'pages': 0, 'previewable': False}
    except DocumentTooBig:
        raise exception_response(509)
    except DocumentUnauthorized:
        raise exception_response(401)
