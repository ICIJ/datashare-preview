import configparser
import os
import sys

from dspreview.cache import DocumentCache
from pathlib import Path
from pydantic import BaseSettings
from typing import Dict, Any


def resolve_conf_path(conf_file: str):
    parent_path = Path(__file__).parent
    return (parent_path / ('../conf/%s' % conf_file)).resolve()


def parse_settings_file(conf_file: str, section: str = 'app:main'):
    conf_path = resolve_conf_path(conf_file)
    config = configparser.ConfigParser()
    config.read(conf_path)
    return config[section] if section in config else None


def configparser_settings(settings: BaseSettings) -> Dict[str, Any]:
    conf_file = settings.__config__.conf_file
    conf_section = settings.__config__.conf_section
    settings = {}
    for field, value in parse_settings_file(conf_file, conf_section).items():
        field_snakecase = field.replace(".", "_")
        settings[field_snakecase] = value
    return settings


class Settings(BaseSettings):
    use: str = "egg:datashare_preview"
    ds_host: str = "http://localhost:8080"
    ds_document_meta_path: str = "/api/index/search/%%s/_doc/%%s"
    ds_document_src_path: str = "/api/%%s/documents/src/%%s"
    ds_document_max_size: int = 50000000
    ds_document_max_age: int = 259200
    ds_session_cookie_enabled: str = "true"
    ds_session_cookie_name: str = "_ds_session_id"
    ds_session_header_enabled: bool = True
    ds_session_header_name: str = "X-Ds-Session-Id"

    class Config:
        conf_file = os.environ.get('DS_CONF_FILE', 'development.ini')
        conf_section = os.environ.get('DS_CONF_SECTION', 'app:main')

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (init_settings, env_settings, configparser_settings, file_secret_settings,)


settings = Settings()
