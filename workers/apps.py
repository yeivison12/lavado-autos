from django.apps import AppConfig

class WorkersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workers'

    def ready(self):
        import workers.signals