from django.db.models import fields


DEFAULT_SETTINGS = {
    # Models to depersonalize
    'MODELS': {
        # app_label.model_name: options
        'django.contrib.auth.models.User', None,
    },
    # Only update (depersonalize) fields of the following types
    'FIELD_TYPES': (fields.CharField, fields.EmailField),
    # Field names to depersonalize
    'FIELD_NAMES':  (
        'name', 'full_name', 'first_name', 'last_name', 'email'
    ),
    'BATCH_SIZE': 1000,
}
