import logging

import pkg_resources
from pyramid.config import Configurator
log = logging.getLogger(__name__)


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_route('home', '/', request_method='GET')
    config.add_route('thumbnail', '/api/v1/thumbnail/{index}/<string:id>', request_method='GET')
    #  config.add_route('thumbnail', '/api/v1/thumbnail/<string:index>/<string:id>.jpg', methods=['GET'])
    config.add_route('info', '/api/v1/thumbnail/{index}/{id}.json', request_method='GET')
    config.scan()
    log.info('launching pserver for datashare preview version %s' % pkg_resources.get_distribution("datashare_preview").version)
    return config.make_wsgi_app()