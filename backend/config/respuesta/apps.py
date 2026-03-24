from django.apps import AppConfig

class RespuestaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'respuesta'

    def ready(self):
        import respuesta.signals