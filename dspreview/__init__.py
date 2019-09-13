import logging

import pkg_resources
from pyramid.config import Configurator
from pyramid.events import NewRequest

log = logging.getLogger(__name__)


def add_cors_headers_response_callback(event):
    def add_cors_headers(request, response):
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'x-ds-session-id',
        })

    event.request.add_response_callback(add_cors_headers)


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_route('home', '/', request_method='GET')
    config.add_route('thumbnail', '/api/v1/thumbnail/{index}/{id}', request_method='GET')
    config.add_route('thumbnail_options', '/api/v1/thumbnail/{index}/{id}', request_method='OPTIONS')
    #  config.add_route('thumbnail', '/api/v1/thumbnail/<string:index>/<string:id>.jpg', methods=['GET'])
    config.add_route('info', '/api/v1/thumbnail/{index}/{id}.json', request_method='GET')
    config.add_route('info_options', '/api/v1/thumbnail/{index}/{id}.json', request_method='OPTIONS')

    config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    config.scan()
    log.info('launching pserver for datashare preview version %s' %
             pkg_resources.get_distribution("datashare_preview").version)
    return config.make_wsgi_app()
