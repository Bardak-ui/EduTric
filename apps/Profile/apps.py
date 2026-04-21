import importlib

from django.apps import AppConfig


class ProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.Profile"  # Или 'apps.Profile', если приложение внутри папки apps

    def ready(self):
        importlib.import_module("apps.Profile.signals")
