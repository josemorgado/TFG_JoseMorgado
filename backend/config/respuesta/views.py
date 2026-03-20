# respuesta/views.py
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    parser_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from quejas.models import Queja               # <-- usa 'quejas' según tu código
from core.permissions import IsModerator      # <-- ya lo tienes en core/permissions.py
from .models import Respuesta
from .serializers import RespuestaSerializer


class SmallResultsSetPagination(PageNumberPagination):
    """
    Paginación simple controlable por query params.
    Por defecto 10 elementos por página.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ============================================================
# GET /quejas/{queja_id}/respuestas/ — Listar (PÚBLICO)
# ============================================================
@extend_schema(
    summary="Listar respuestas de una queja",
    description="Devuelve la lista paginada de respuestas oficiales de la queja indicada.",
    tags=["Respuestas"],
    parameters=[
        OpenApiParameter(
            name="queja_id",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name="page",
            type=int,
            description="Número de página",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description="Tamaño de página (máx. 50)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={200: OpenApiResponse(response=RespuestaSerializer(many=True))},
)
@api_view(['GET'])
@authentication_classes([])              # GET público, no hace falta JWT
@permission_classes([AllowAny])
def respuestas_listar(request, queja_id: int):
    """
    LISTA PÚBLICA de respuestas de una queja.
    """
    queja = get_object_or_404(Queja, pk=queja_id)
    qs = (
        Respuesta.objects
        .filter(queja=queja)
        .select_related('moderador')
        .order_by('-fecha_respuesta')
    )

    paginator = SmallResultsSetPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = RespuestaSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


# ============================================================
# POST /quejas/{queja_id}/respuestas/crear/ — Crear (SOLO MODERADOR)
# ============================================================
@extend_schema(
    summary="Crear respuesta (solo moderadores)",
    description=(
        "Crea una respuesta oficial asociada a la queja. "
        "Si se provee `nuevo_estado` ('PEN'|'ENP'|'RES'|'REC'), la queja cambia a ese estado de forma atómica."
    ),
    tags=["Respuestas"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "contenido": {"type": "string"},
                "nuevo_estado": {"type": ["string", "null"], "enum": ["PEN", "ENP", "RES", "REC", None]},
            },
            "required": ["contenido"],
            "example": {
                "contenido": "Tras la inspección, se programa reparación para mañana.",
                "nuevo_estado": "ENP",
            },
        }
    },
    responses={
        201: OpenApiResponse(response=RespuestaSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Se requieren permisos de moderador"),
        404: OpenApiResponse(description="Queja no encontrada"),
    },
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])     # ← necesitamos conocer al usuario
@permission_classes([IsAuthenticated, IsAdminUser])  # ← SOLO moderadores pueden crear
@parser_classes([JSONParser])
def respuesta_crear(request, queja_id: int):
    """
    CREACIÓN RESTRINGIDA a moderadores.
    - Valida JSON.
    - Usa transacción + select_for_update() para aplicar, si corresponde, el cambio de estado en la queja.
    """
    contenido = (request.data.get("contenido") or "").strip()
    nuevo_estado = request.data.get("nuevo_estado")

    if not contenido:
        return Response(
            {"contenido": ["Este campo no puede estar vacío."]},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        # select_for_update() evita condiciones de carrera cuando se cambia el estado
        queja = (
            Queja.objects
            .select_for_update()
            .filter(pk=queja_id)
            .first()
        )
        if not queja:
            return Response({"detail": "La queja no existe."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RespuestaSerializer(data={"contenido": contenido, "nuevo_estado": nuevo_estado})
        serializer.is_valid(raise_exception=True)

        respuesta = serializer.save(moderador=request.user, queja=queja)

        # Si la respuesta define nuevo estado, lo aplicamos a la queja
        if respuesta.nuevo_estado:
            queja.estado = respuesta.nuevo_estado
            queja.save(update_fields=['estado', 'fecha_actualizacion'])

        return Response(RespuestaSerializer(respuesta).data, status=status.HTTP_201_CREATED)


# ============================================================
# GET /respuestas/{respuesta_id}/ — Detalle (PÚBLICO)
# ============================================================
@extend_schema(
    summary="Detalle de una respuesta (público)",
    description="Devuelve la respuesta solicitada.",
    tags=["Respuestas"],
    parameters=[
        OpenApiParameter(
            name="respuesta_id",
            type=int,
            description="ID de la respuesta",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=RespuestaSerializer),
        404: OpenApiResponse(description="Respuesta no encontrada"),
    },
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def respuesta_detalle_publico(request, respuesta_id: int):
    """
    DETALLE PÚBLICO de una respuesta.
    """
    respuesta = get_object_or_404(Respuesta.objects.select_related('queja', 'moderador'), pk=respuesta_id)
    return Response(RespuestaSerializer(respuesta).data, status=status.HTTP_200_OK)


# ============================================================
# PATCH/PUT/DELETE /respuestas/{respuesta_id}/ — Editar/Eliminar (SOLO MODERADOR)
# ============================================================
@extend_schema(
    summary="Editar o eliminar respuesta (solo moderadores)",
    description=(
        "PATCH/PUT: Actualiza la respuesta. Si llega `nuevo_estado`, se aplica a la queja de forma atómica.\n"
        "DELETE: Elimina la respuesta."
    ),
    tags=["Respuestas"],
    request=RespuestaSerializer,
    parameters=[
        OpenApiParameter(
            name="respuesta_id",
            type=int,
            description="ID de la respuesta",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=RespuestaSerializer),
        204: OpenApiResponse(description="Eliminado"),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Se requieren permisos de moderador"),
        404: OpenApiResponse(description="Respuesta no encontrada"),
    },
)
@api_view(['PUT', 'PATCH', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsModerator])   # ← SOLO moderadores
@parser_classes([JSONParser])
def respuesta_admin(request, respuesta_id: int):
    """
    OPERACIONES RESTRINGIDAS a moderadores:
    - PUT/PATCH: actualiza la respuesta (contenido/estado).
    - DELETE: elimina la respuesta.
    Todo cambio de estado se realiza en transacción con bloqueo de la queja.
    """
    respuesta = get_object_or_404(Respuesta.objects.select_related('queja'), pk=respuesta_id)

    # ---- PUT / PATCH ----
    if request.method in ('PUT', 'PATCH'):
        parcial = request.method == 'PATCH'
        with transaction.atomic():
            serializer = RespuestaSerializer(respuesta, data=request.data, partial=parcial)
            serializer.is_valid(raise_exception=True)

            respuesta = serializer.save()

            # Si se envía nuevo_estado, aplicarlo a la queja bajo bloqueo
            nuevo_estado = serializer.validated_data.get("nuevo_estado", None)
            if nuevo_estado:
                queja = (
                    Queja.objects
                    .select_for_update()
                    .get(pk=respuesta.queja_id)
                )
                queja.estado = nuevo_estado
                queja.save(update_fields=['estado', 'fecha_actualizacion'])

            return Response(RespuestaSerializer(respuesta).data, status=status.HTTP_200_OK)

    # ---- DELETE ----
    respuesta.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
