import configparser
import sys

from dspreview import read_settings_in_environements
from dspreview.cache import DocumentCache
from pathlib import Path


def resolve_settings_path(settings_file):
    parent_path = Path(__file__).parent
    return (parent_path / ('../conf/%s' % settings_file)).resolve()


def parse_settings_file(settings_file, section = 'app:main'):
    settings_path = resolve_settings_path(settings_file)
    config = configparser.ConfigParser()
    config.read(settings_path)
    return config[section] if section in config else None


def get_settings(settings_file):
    settings = parse_settings_file(settings_file)
    return read_settings_in_environements(settings)


def main():
    settings_file = (sys.argv[1:] or ['development.ini'])[0]
    settings = get_settings(settings_file)
    max_age = int(settings['ds.document.max.age'])
    DocumentCache(max_age).purge()


if __name__ == '__main__':
    main()
