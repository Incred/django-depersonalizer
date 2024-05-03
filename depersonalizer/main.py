import logging
from multiprocessing import Pool

from django.apps import apps
from django.db.models import fields
from django import db

from .conf import settings
from .data_source import DataSource


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


class Depersonalizer:
    data_source = None
    options = None
    field_types_to_update = settings.FIELD_TYPES
    additional_field_source_map = settings.ADDITIONAL_FIELD_SOURCE_MAP

    def __init__(self, data_source=None, options=options):
        if options is None:
            options = {}
        if data_source is None:
            unique_fields = options.get('unique_fields')
            additional_field_source_map = self.additional_field_source_map
            additional_field_names = options.get('field_names', tuple())
            self.field_names_to_update = settings.FIELD_NAMES + additional_field_names
            self._data_source = DataSource(
                unique_fields=unique_fields,
                additional_field_source_map=additional_field_source_map
            )

    def _is_appropriate_field(self, field_obj):
        return (isinstance(field_obj, self.field_types_to_update) and
                field_obj.name in self.field_names_to_update)

    def get_field_names_to_update(self, model):
        field_names_to_update = set()
        for field in model._meta.get_fields():
            if self._is_appropriate_field(field):
                field_names_to_update.add(field.name)
        return field_names_to_update

    def update_object(self, model_object, field_names):
        for field_name in field_names:
            field_value = getattr(self._data_source, field_name)
            setattr(model_object, field_name, field_value)
        return model_object

    def get_model_objects(self, model):
        return model._base_manager.iterator()

    def process_model(self, model):
        field_names_to_update = self.get_field_names_to_update(model)
        if not field_names_to_update:
            logger.info('No fields to update for %s model', model)
            return
        model_objects = set()
        for model_object in self.get_model_objects(model):
            model_object = self.update_object(model_object, field_names_to_update)
            model_objects.add(model_object)
        model.objects.bulk_update(
            model_objects,
            field_names_to_update, batch_size=settings.BATCH_SIZE
        )
        logger.info('Updated %s objects of %s', len(model_objects), model)


def get_all_models():
    for model in apps.get_models():
        model_name = f'{model._meta.app_label}.{model.__name__}'
        if model_name in settings.MODELS:
            yield model, settings.MODELS[model_name]


def run(model, options):
    logger.info('Start processing %s model', model)
    depersonalizer = Depersonalizer(options=options)
    depersonalizer.process_model(model)
    logger.info('Processing %s model done', model)


def check_config():
    # need to check if all fields have source mapping
    field_names = list(settings.FIELD_NAMES)
    for model, options in settings.MODELS.items():
        if options is None:
            continue
        field_names.extend(options.get("field_names", list()))
    field_source_maps = settings.FIELD_SOURCE_MAP | settings.ADDITIONAL_FIELD_SOURCE_MAP
    for field_name in field_names:
        if field_name not in field_source_maps:
            raise ConfigurationError(f'Field "{field_name}" doesn\'t have source!')


def run_depersonalization(dry_run=True):
    # need to close all db connection to make it possible to run using multiprocessing
    check_config()
    db.connections.close_all()
    with Pool(processes=1) as pool:
        pool.starmap(run, get_all_models())
