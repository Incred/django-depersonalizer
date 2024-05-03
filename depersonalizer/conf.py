from typing import Any

from django.conf import settings as django_settings

from .settings import DEFAULT_SETTINGS

SETTINGS_PREFIX = getattr(django_settings, 'DEPERSONALIZER_SETTINGS_PREFIX', 'DEPERSONALIZER')


class Settings:
    default_settings: dict = {}

    def __init__(self, default_settings: dict):
        self.default_settings = default_settings

    def _get_setting(self, setting_name: str, default_value: Any) -> Any:
        setting_name = f'{SETTINGS_PREFIX}_{setting_name}'
        return getattr(django_settings, setting_name, default_value)

    def __getattr__(self, attr: str):
        default_value = self.default_settings.get(attr)
        setting_value = self._get_setting(attr, default_value)
        return setting_value


settings = Settings(default_settings=DEFAULT_SETTINGS)
