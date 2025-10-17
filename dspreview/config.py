import os
import configparser

from pathlib import Path
from typing import Any, Dict, Tuple
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource


class ConfigParserSettingsSource(PydanticBaseSettingsSource):
    """
    Custom settings source that loads configuration values from an INI file.
    """

    def __init__(self, settings_cls: type[BaseSettings], ini_file: Path, section: str = "app:main"):
        super().__init__(settings_cls)
        self.ini_file = ini_file
        self.section = section
        self._data = self._load_ini()

    def _load_ini(self) -> Dict[str, Any]:
        """Parse the INI file and return key/value pairs."""
        if not self.ini_file.exists():
            return {}

        parser = configparser.ConfigParser()
        parser.read(self.ini_file)

        if self.section not in parser:
            return {}

        data: Dict[str, Any] = {}
        for key, value in parser[self.section].items():
            data[key.replace(".", "_")] = value
        return data

    # Required by Pydantic v2
    def get_field_value(self, field_name: str, field: FieldInfo) -> Tuple[Any, str | None]:
        """
        Return a tuple (value, source) for a specific field.
        """
        if field_name in self._data:
            return self._data[field_name], self.ini_file.as_posix()
        return None, None

    # Optional convenience: used when returning all values at once
    def __call__(self) -> Dict[str, Any]:
        return self._data


class Settings(BaseSettings):
    """
    Application settings loaded from:
      1. init arguments
      2. environment variables (.env)
      3. a single INI file defined by DS_CONF_FILE
      4. defaults here
    """

    ds_host: str = "http://localhost:8080"
    ds_document_meta_path: str = "/api/index/search/%s/_doc/%s"
    ds_document_src_path: str = "/api/%s/documents/src/%s"
    ds_document_max_size: int = 50_000_000
    ds_document_max_age: int = 259_200
    ds_session_cookie_enabled: bool = True
    ds_session_cookie_name: str = "_ds_session_id"
    ds_session_header_enabled: bool = True
    ds_session_header_name: str = "X-Ds-Session-Id"

    model_config = SettingsConfigDict(
        env_prefix="DS_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
        conf_file=os.environ.get("DS_CONF_FILE", "conf/development.ini"),
        conf_section=os.environ.get("DS_CONF_SECTION", "app:main"),
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """
        Load order:
          1. init args
          2. env / .env
          3. INI file (if present)
          4. file secrets
        """
        conf_file = os.environ.get("DS_CONF_FILE", cls.model_config.get("conf_file"))
        conf_section = os.environ.get("DS_CONF_SECTION", cls.model_config.get("conf_section"))

        sources = [init_settings, env_settings, dotenv_settings]

        if conf_file:
            path = Path(conf_file)
            if path.exists():
                sources.append(ConfigParserSettingsSource(settings_cls, ini_file=path, section=conf_section))

        sources.append(file_secret_settings)
        return tuple(sources)

settings = Settings()