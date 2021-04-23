import configparser
import os
import sys

from fastapi.logger import logger
from dspreview.cache import DocumentCache
from pathlib import Path
from pydantic import BaseSettings
from typing import Dict, Any


def parse_settings_file(conf_file: str, section: str = 'app:main') -> dict:
    conf_path = Path(conf_file).resolve()
    config = configparser.ConfigParser()
    config.read(conf_path)
    if section in config:
        logger.info('Loaded configuration from %s' % conf_path)
        return config[section]
    return {}


def configparser_settings(settings: BaseSettings) -> Dict[str, Any]:
    conf_file = settings.__config__.conf_file
    conf_section = settings.__config__.conf_section
    settings = {}
    for field, value in parse_settings_file(conf_file, conf_section).items():
        field_snakecase = field.replace(".", "_")
        settings[field_snakecase] = value
    return settings


class Settings(BaseSettings):
    ds_host: str = "http://localhost:8080"
    ds_document_meta_path: str = "/api/index/search/%s/_doc/%s"
    ds_document_src_path: str = "/api/%s/documents/src/%s"
    ds_document_max_size: int = 50000000
    ds_document_max_age: int = 259200
    ds_session_cookie_enabled: str = "true"
    ds_session_cookie_name: str = "_ds_session_id"
    ds_session_header_enabled: bool = True
    ds_session_header_name: str = "X-Ds-Session-Id"

    class Config:
        conf_file = os.environ.get('DS_CONF_FILE', 'conf/development.ini')
        conf_section = os.environ.get('DS_CONF_SECTION', 'app:main')

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (init_settings, env_settings, configparser_settings, file_secret_settings,)


settings = Settings()
