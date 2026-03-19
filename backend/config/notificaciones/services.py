from .models import Notificacion
from django.db import transaction

def crear_notificacion(*,user,title:str,message:str,url:str|None=None):
    if not user:
        return
    def _create():
        Notificacion.objects.create(
            user=user,
            title=title[:255],
            message=message,
            url=url,
        )

    transaction.on_commit(_create)