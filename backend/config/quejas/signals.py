from notificaciones.services import crear_notificacion
from django.db.models.signals import post_save
from django.dispatch import receiver
from comentario.models import Comentario
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.module_loading import import_string

from notificaciones.services import crear_notificacion

from quejas.models import Queja
from comentario.models import Comentario
from megusta.models import MeGusta


def obtener_comentario_root(comentario):
    root = comentario
    while root.parent is not None:
        root = root.parent
    return root


@receiver(post_save, sender=Comentario)
def notificar_comentarios(sender, instance, created, **kwargs):
    # Si es nivel 0 se notifica al creador de la queja
    # Si es respuesta a comentario se notifica al creador del com padre de la respuesta, al creador del comentario nivel 0 de la respuesta y al creador de la queja
    if not created:
        return
    comentario = instance
    autor_accion = comentario.autor
    queja = comentario.queja
    autor_queja = queja.autor
    # Caso 1 comentario nivel 0
    if comentario.parent is None:
        if autor_accion != autor_queja:
            crear_notificacion(
                user=autor_queja,
                title="Nuevo comentario en tu queja",
                message=f"{autor_accion.username} ha comentado en tu queja.",
                url=f"http://localhost:5173/quejas/{queja.id}",
            )
        return
    # Caso 2 respuesta a comentario
    comentario_padre = comentario.parent
    autor_padre = comentario_padre.autor
    comentario_root = obtener_comentario_root(comentario)
    autor_root = comentario_root.autor
    if autor_accion != autor_padre:
        crear_notificacion(
            user=autor_padre,
            title="Nueva respuesta a tu comentario.",
            message=f"{autor_accion.username} ha respondido a tu comentario.",
            url=f"http://localhost:5173/quejas/{queja.id}",
        )
    if autor_root not in (autor_padre, autor_accion):
        crear_notificacion(
            user=autor_root,
            title="Nueva respuesta en el hilo.",
            message=f"{autor_accion.username} ha respondido en un hilo en el que participas.",
            url=f"http://localhost:5173/quejas/{queja.id}",
        )
    if autor_queja not in (autor_root, autor_padre, autor_accion):
        crear_notificacion(
            user=autor_queja,
            title="Nueva respuesta en tu queja.",
            message=f"{autor_accion.username} ha respondido en un hilo de tu queja.",
            url=f"http://localhost:5173/quejas/{queja.id}",
        )


@receiver(post_save, sender=MeGusta)
def notificar_megusta(sender, instance: MeGusta, created: bool, **kwargs):
    if not created:
        return

    actor = instance.autor
    obj = instance.content_object

    if obj is None:
        return

    if isinstance(obj, Queja):
        autor_destino = getattr(obj, "autor", None)
        if autor_destino and autor_destino != actor:
            crear_notificacion(
                user=autor_destino,
                title="Nuevo me gusta en tu queja",
                message=f"A {actor.username} le ha gustado tu queja.",
                url=f"/quejas/{obj.id}",
            )
        return

    if isinstance(obj, Comentario):
        autor_destino = getattr(obj, "autor", None)
        if autor_destino and autor_destino != actor:
            crear_notificacion(
                user=autor_destino,
                title="Nuevo me gusta en tu comentario",
                message=f"A {actor.username} le ha gustado tu comentario.",
                url=f"/quejas/{obj.queja.id}#comentario-{obj.id}",
            )
        return

