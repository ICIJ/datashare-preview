import pkg_resources
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='home')
def home(_):
    return Response(content_type='text/plain', body='Datashare preview v%s' % pkg_resources.get_distribution("datashare_preview").version)


@view_config(route_name='thumbnail')
def thumbnail(request):
    return Response(content_type='text/plain', body='')


@view_config(route_name='info')
def info(request):
    return Response(content_type='text/plain', body='')
