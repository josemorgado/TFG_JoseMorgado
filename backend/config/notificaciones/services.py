from .models import Notificacion
from django.db import transaction

def crear_notificacion(*, user, title: str, message: str, url: str | None = None):
    if not user:
        print(">>> crear_notificacion: user=None, no se crea notificación")
        return

    def _create():
        print(">>> Ejecutando _create de crear_notificacion()")  # DEBUG
        Notificacion.objects.create(
            user=user,
            title=title[:255],
            message=message,
            url=url,
        )

    print(">>> registrando on_commit")  # DEBUG
    transaction.on_commit(_create)