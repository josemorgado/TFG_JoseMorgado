# suggestions/views.py

from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view, permission_classes, authentication_classes
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.db.models import Count

from core.permissions import IsAuthorOrModerator, IsModerator
from suggestion.models import Suggestion
from suggestion.serializers import SuggestionSerializer

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

User = get_user_model()


# -------------------------------------------------------------
# Permisos manuales como haces en quejas
# -------------------------------------------------------------
def _enforce_object_permissions(request, obj):
    """
    Ejecuta permisos de objeto MANUALMENTE igual que con quejas.
    """
    perm = IsAuthorOrModerator()
    if hasattr(perm, "has_object_permission"):
        if not perm.has_object_permission(request, view=None, obj=obj):
            raise PermissionDenied(detail="No tienes permisos para modificar esta sugerencia.")


# -------------------------------------------------------------
# GET /suggestions/ → Listar sugerencias
# -------------------------------------------------------------
@extend_schema(
    summary="Listar sugerencias",
    description="Devuelve un listado completo de sugerencias ordenadas por ID ascendente.",
    tags=["Sugerencias"],
    responses={200: OpenApiResponse(response=SuggestionSerializer(many=True))},
)
@api_view(['GET'])
@permission_classes([AllowAny])
def suggestions_list(request):
    qs = Suggestion.objects.order_by('id')
    serializer = SuggestionSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


# -------------------------------------------------------------
# GET /suggestions/<pk>/ → Detalle
# -------------------------------------------------------------
@extend_schema(
    summary="Obtener detalle de una sugerencia",
    description="Retorna los datos completos de una sugerencia.",
    tags=["Sugerencias"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la sugerencia",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: SuggestionSerializer,
        404: OpenApiResponse(description="No encontrada"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def suggestion_detail(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    serializer = SuggestionSerializer(suggestion, context={'request': request})
    return Response(serializer.data)


# -------------------------------------------------------------
# POST /suggestions/create/ → Crear sugerencia
# -------------------------------------------------------------
@extend_schema(
    summary="Crear sugerencia",
    description="Crea una sugerencia nueva.",
    tags=["Sugerencias"],
    request=SuggestionSerializer,
    responses={
        201: SuggestionSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de creación",
            value={
                "titulo": "Mejorar zonas verdes",
                "descripcion": "Sería buena idea añadir más árboles en el parque central."
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suggestion_create(request):
    serializer = SuggestionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        obj = serializer.save()
        return Response(SuggestionSerializer(obj).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------
# PUT /suggestions/<pk>/update/ → Actualizar sugerencia
# -------------------------------------------------------------
@extend_schema(
    summary="Actualizar sugerencia (completo)",
    description="Actualiza completamente una sugerencia.",
    tags=["Sugerencias"],
    request=SuggestionSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la sugerencia",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: SuggestionSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="No encontrada"),
    },
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def suggestion_update(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    _enforce_object_permissions(request, suggestion)

    serializer = SuggestionSerializer(suggestion, data=request.data, context={'request': request})
    if serializer.is_valid():
        obj = serializer.save()
        return Response(SuggestionSerializer(obj).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------
# DELETE /suggestions/<pk>/delete/ → Eliminar sugerencia
# -------------------------------------------------------------
@extend_schema(
    summary="Eliminar sugerencia",
    description="Elimina una sugerencia por su ID.",
    tags=["Sugerencias"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la sugerencia",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Sugerencia eliminada"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="No encontrada"),
    },
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def suggestion_delete(request, pk):
    suggestion = get_object_or_404(Suggestion, pk=pk)
    _enforce_object_permissions(request, suggestion)

    suggestion.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------------------------------------
# GET /suggestions/autor/<autor_id>/ → Filtrar por autor
# -------------------------------------------------------------
@extend_schema(
    summary="Listar sugerencias por autor",
    description="Devuelve las sugerencias creadas por un usuario concreto.",
    tags=["Sugerencias"],
    parameters=[
        OpenApiParameter(
            name="autor_id",
            type=int,
            description="ID del autor",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={200: SuggestionSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([AllowAny])
def suggestions_por_autor(request, autor_id):
    qs = Suggestion.objects.filter(autor_id=autor_id).order_by('id')
    serializer = SuggestionSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)