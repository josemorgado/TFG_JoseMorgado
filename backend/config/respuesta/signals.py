from django.db.models.signals import post_save
from django.dispatch import receiver

from respuesta.models import Respuesta
from notificaciones.services import crear_notificacion


@receiver(post_save, sender=Respuesta)
def notificar_respuesta_formal(sender, instance, created, **kwargs):

    if not created:
        return

    respuesta = instance
    queja = respuesta.queja
    autor_queja = queja.autor
    moderador = respuesta.moderador


    estado_msg = (
        f" La queja ha pasado al estado '{respuesta.nuevo_estado}'."
        if respuesta.nuevo_estado else ""
    )

    crear_notificacion(
        user=autor_queja,
        title="Nueva respuesta oficial a tu queja",
        message=f"El moderador {moderador.username} ha emitido una respuesta oficial." + estado_msg,
        url=f"/quejas/{queja.id}/respuestas/",
    )