# Django Depersonalizer (Obfuscator)

Ddjango data obfuscation app.

Add configuration to settings.py, e.g.:

DEPERSONALIZER_SETTINGS_PREFIX = "DEPERSONALIZER"
DEPERSONALIZER_MODELS = {
    # app_label.model_name: options
    'myapp1.MyModel': None,
    'myapp2.MyNewModel': {"unique_fields": ("name", "email")},
    'myapp3.SuperNewModel': {
        "field_names": ("company_name",) # additional field to depersonalize
    },
}
DEPERSONALIZER_ADDITIONAL_FIELD_SOURCE_MAP = {
    "company_name": "finance.company", # source for this field
}
