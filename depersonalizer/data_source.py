from uuid import uuid4
from mimesis import Generic
from mimesis.locales import Locale


class GenericDataProvider(Generic):
    pass


class DataSource:
    # each field can be unique
    unique_fields = ()

    def __init__(
            self,
            source=None,
            unique_fields=None,
            additional_field_source_map=None
    ):
        from .conf import settings
        self.field_source_map = settings.FIELD_SOURCE_MAP
        if additional_field_source_map is not None:
            self.field_source_map |= additional_field_source_map
        if source is None:
            source = GenericDataProvider(locale=Locale.RU)
        self._source = source
        if unique_fields is not None:
            self.unique_fields = unique_fields

    def _get_source_func(self, attr, source=None):
        attrs = attr.split('.')
        if source is None:
            source = self._source
        if len(attrs) == 1:
            return getattr(source, attrs[0])
        source = getattr(source, attrs[0])
        return self._get_source_func(
            attr=".".join(attrs[1:]),
            source=source
        )

    def _is_unique(self, field_name):
        return field_name in self.unique_fields

    def __getattr__(self, item):
        source_provider_path = self.field_source_map[item]
        source_func = self._get_source_func(attr=source_provider_path)
        field_value = source_func()
        if self._is_unique(item):
            field_value = f'{field_value} ({uuid4()})'
        return field_value
