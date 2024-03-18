import logging
from multiprocessing import Pool

from django.apps import apps
from django.db.models import fields
from django import db

from .data_source import DataSource
from .conf import settings


logger = logging.getLogger(__name__)


class Depersonalizer:
    data_source = None
    options = None
    field_types_to_update = settings.FIELD_TYPES
    field_names_to_update = settings.FIELD_NAMES

    def __init__(self, data_source=None, options=options):
        if options is None:
            options = {}
        if data_source is None:
            unique_fields = options.get('unique_fields')
            self._data_source = DataSource(unique_fields=unique_fields)

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
            field_names_to_update,batch_size=settings.BATCH_SIZE
        )


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


def run_depersonalization(dry_run=True):
    # need to close all db connection to make it possible to run using multiprocessing
    db.connections.close_all()
    with Pool(processes=4) as pool:
        pool.starmap(run, get_all_models())
