from django.apps import apps
from django.contrib import admin


# Get all models for the current app
app_models = apps.get_app_config(__name__.split('.')[-2]).get_models()

# Register models dynamically
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # Skip if already registered