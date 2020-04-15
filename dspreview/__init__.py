import logging

import pkg_resources
import os
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


def read_settings_in_environements(settings, prefix='DS_'):
    for (env_key, value) in os.environ.items():
        if env_key.upper().startswith(prefix.upper()):
            settings_key = '.'.join(env_key.lower().split('_'))
            settings[settings_key] = value
    settings['server_main_port'] = "6543"
    return expandvars_dict(settings)


def expandvars_dict(settings):
    return dict((k, os.path.expandvars(value)) for k, value in settings.items())


def main(global_config, **settings):
    settings = read_settings_in_environements(settings)
    config = Configurator(settings=settings)

    config.add_route('home', '/', request_method='GET')
    config.add_route('info', '/api/v1/thumbnail/{index}/{id}.json', request_method='GET')
    config.add_route('info_options', '/api/v1/thumbnail/{index}/{id}.json', request_method='OPTIONS')
    config.add_route('thumbnail', '/api/v1/thumbnail/{index}/{id}', request_method='GET')
    config.add_route('thumbnail_options', '/api/v1/thumbnail/{index}/{id}', request_method='OPTIONS')
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
    config.scan()

    version = pkg_resources.get_distribution("datashare_preview").version
    log.info('launching pserver for datashare preview version %s' % version)
    
    return config.make_wsgi_app()
