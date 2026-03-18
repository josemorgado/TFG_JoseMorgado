from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample
)

from .models import Notificacion
from .serializers import NotificacionSerializer, NotificacionCreateSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================
# GET /notifications/ — Listado paginado (con filtro is_read)
# ============================================================
@extend_schema(
    summary="Listar notificaciones del usuario autenticado",
    description=(
        "Devuelve la lista **paginada** de notificaciones pertenecientes al usuario "
        "autenticado, ordenadas por fecha de creación descendente.\n\n"
        "Permite filtrar por el estado de lectura usando el query param `is_read`.\n\n"
        "**Query params**:\n"
        "- `is_read`: `true|1` para solo leídas, `false|0` para solo no leídas\n"
        "- `page`: número de página (paginación estándar DRF)\n"
        "- `page_size`: tamaño de página (máx. 100)\n"
    ),
    tags=["Notificaciones"],
    parameters=[
        OpenApiParameter(
            name="is_read",
            type=str,
            description="Filtrado: `true|1` solo leídas, `false|0` solo no leídas",
            required=False,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page",
            type=int,
            description="Número de página para la paginación",
            required=False,
            location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description="Tamaño de página (máximo 100)",
            required=False,
            location=OpenApiParameter.QUERY
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=NotificacionSerializer(many=True),
            description="Listado paginado de notificaciones"
        ),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Respuesta paginada (solo no leídas)",
            value={
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 15,
                        "user": 3,
                        "title": "Nueva respuesta del alcalde",
                        "message": "Se ha publicado una respuesta a tu queja #42",
                        "created_at": "2026-03-18T10:35:12Z",
                        "is_read": False,
                        "url": "/quejas/42"
                    },
                    {
                        "id": 14,
                        "user": 3,
                        "title": "Queja actualizada",
                        "message": "Tu queja #40 ha pasado a EN PROCESO",
                        "created_at": "2026-03-18T09:10:05Z",
                        "is_read": False,
                        "url": "/quejas/40"
                    }
                ]
            },
            response_only=True
        )
    ],
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    Lista paginada de notificaciones del usuario.
    Filtros opcionales: ?is_read=true|false
    """
    qs = Notification.objects.filter(user=request.user).order_by('-created_at')

    is_read = request.query_params.get('is_read')
    if is_read is not None:
        if is_read.lower() in ('true', '1'):
            qs = qs.filter(is_read=True)
        elif is_read.lower() in ('false', '0'):
            qs = qs.filter(is_read=False)

    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = NotificationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


# ============================================================
# GET /notifications/unread-count/ — Contador no leídas
# ============================================================
@extend_schema(
    summary="Contador de notificaciones no leídas",
    description="Devuelve el número total de notificaciones **no leídas** del usuario autenticado.",
    tags=["Notificaciones"],
    responses={
        200: OpenApiResponse(
            description="Contador devuelto correctamente",
            examples=[
                OpenApiExample(
                    "Ejemplo conteo",
                    value={"unread": 3},
                    response_only=True
                )
            ]
        ),
        401: OpenApiResponse(description="No autenticado"),
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_unread_count(request):
    """
    Devuelve el total de notificaciones no leídas del usuario.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread': count}, status=200)


# ============================================================
# PATCH /notifications/{id}/read/ — Marcar como leída
# ============================================================
@extend_schema(
    summary="Marcar notificación como leída",
    description="Marca como **leída** una notificación que pertenezca al usuario autenticado.",
    tags=["Notificaciones"],
    parameters=[
        OpenApiParameter(
            name="notification_id",
            type=int,
            description="ID de la notificación a marcar como leída",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Notificación marcada como leída",
            examples=[OpenApiExample("OK", value={"detail": "Marcada como leída"}, response_only=True)]
        ),
        401: OpenApiResponse(description="No autenticado"),
        404: OpenApiResponse(description="Notificación no encontrada"),
    }
)
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, notification_id):
    """
    Marca una notificación del usuario como leída.
    """
    try:
        n = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        return Response({'detail': 'Notificación no encontrada'}, status=404)

    n.is_read = True
    n.save(update_fields=['is_read'])
    return Response({'detail': 'Marcada como leída'}, status=200)


# ============================================================
# PATCH /notifications/{id}/unread/ — Marcar como NO leída
# ============================================================
@extend_schema(
    summary="Marcar notificación como NO leída",
    description="Marca como **no leída** una notificación que pertenezca al usuario autenticado.",
    tags=["Notificaciones"],
    parameters=[
        OpenApiParameter(
            name="notification_id",
            type=int,
            description="ID de la notificación a marcar como no leída",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Notificación marcada como no leída",
            examples=[OpenApiExample("OK", value={"detail": "Marcada como no leída"}, response_only=True)]
        ),
        401: OpenApiResponse(description="No autenticado"),
        404: OpenApiResponse(description="Notificación no encontrada"),
    }
)
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_mark_unread(request, notification_id):
    """
    Marca una notificación del usuario como NO leída.
    """
    try:
        n = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        return Response({'detail': 'Notificación no encontrada'}, status=404)

    n.is_read = False
    n.save(update_fields=['is_read'])
    return Response({'detail': 'Marcada como no leída'}, status=200)


# ============================================================
# PATCH /notifications/read-all/ — Marcar todas como leídas
# ============================================================
@extend_schema(
    summary="Marcar todas las notificaciones como leídas",
    description="Marca **todas** las notificaciones del usuario autenticado como leídas.",
    tags=["Notificaciones"],
    responses={
        200: OpenApiResponse(
            description="Operación realizada",
            examples=[OpenApiExample("OK", value={"detail": "Todas marcadas como leídas"}, response_only=True)]
        ),
        401: OpenApiResponse(description="No autenticado"),
    }
)
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_mark_all_read(request):
    """
    Marca todas las notificaciones del usuario como leídas.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'detail': 'Todas marcadas como leídas'}, status=200)


# ============================================================
# DELETE /notifications/{id}/ — Eliminar una notificación
# ============================================================
@extend_schema(
    summary="Eliminar una notificación del propio usuario",
    description="Elimina una notificación que **pertenezca al usuario autenticado**.",
    tags=["Notificaciones"],
    parameters=[
        OpenApiParameter(
            name="notification_id",
            type=int,
            description="ID de la notificación a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Notificación eliminada"),
        401: OpenApiResponse(description="No autenticado"),
        404: OpenApiResponse(description="Notificación no encontrada"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_delete(request, notification_id):
    """
    Elimina una notificación del propio usuario.
    """
    try:
        n = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        return Response({'detail': 'Notificación no encontrada'}, status=404)
    n.delete()
    return Response(status=204)


# ============================================================
# POST /notifications/create/ — Crear (admin/uso interno)
# ============================================================
@extend_schema(
    summary="Crear una notificación (solo admin)",
    description=(
        "Crea una notificación para cualquier usuario. **Restringido a administradores**.\n\n"
        "Body esperado (JSON): `user`, `title`, `message`, `url` (opcional)"
    ),
    tags=["Notificaciones"],
    request=NotificacionCreateSerializer,
    responses={
        201: OpenApiResponse(response=NotificacionCreateSerializer, description="Notificación creada"),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
    },
    examples=[
        OpenApiExample(
            "Crear notificación de actualización de queja",
            value={
                "user": 5,
                "title": "Estado actualizado",
                "message": "Tu queja #42 pasó a EN PROCESO",
                "url": "/quejas/42"
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def notification_create(request):
    """
    Crea una notificación (para cualquier usuario).
    Protegido para admin o para uso interno.
    """
    serializer = NotificationCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
