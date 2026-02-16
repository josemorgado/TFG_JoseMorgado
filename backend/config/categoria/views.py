from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from core.permissions import IsModerator
from categoria.models import Categoria
from categoria.serializers import CategoriaSerializer


# ============================================================
# GET /categorias/ — Listado de categorías
# ============================================================
@extend_schema(
    summary="Listar categorías",
    description="Devuelve un listado completo de todas las categorías ordenadas por su ID.",
    tags=["Categorías"],
    responses={
        200: OpenApiResponse(response=CategoriaSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def categoria_list(request):
    qs = Categoria.objects.all().order_by('id')
    serializer = CategoriaSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /categorias/{pk}/ — Detalle de una categoría
# ============================================================
@extend_schema(
    summary="Obtener detalle de una categoría",
    description="Retorna los datos completos de una categoría dado su identificador.",
    tags=["Categorías"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la categoría a consultar",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=CategoriaSerializer),
        404: OpenApiResponse(description="Categoría no encontrada"),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def categoria_detail(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    serializer = CategoriaSerializer(categoria)
    return Response(serializer.data)


# ============================================================
# POST /categorias/create/ — Crear categoría
# ============================================================
@extend_schema(
    summary="Crear nueva categoría",
    description="Permite crear una categoría. Solo disponible para usuarios con rol de moderador.",
    tags=["Categorías"],
    request=CategoriaSerializer,
    responses={
        201: OpenApiResponse(response=CategoriaSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de request",
            value={"nombre": "Transporte", "descripcion": "Incidencias sobre transporte público"},
            request_only=True
        ),
        OpenApiExample(
            "Ejemplo de response (201)",
            value={"id": 1, "nombre": "Transporte", "descripcion": "Incidencias sobre transporte público"},
            response_only=True
        ),
    ],
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsModerator])
def categoria_create(request):
    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        categoria = serializer.save()
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# PUT /categorias/{pk}/update/ — Actualizar categoría
# ============================================================
@extend_schema(
    summary="Actualizar categoría",
    description="Actualiza todos los campos de una categoría existente.",
    tags=["Categorías"],
    request=CategoriaSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la categoría a actualizar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=CategoriaSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        404: OpenApiResponse(description="Categoría no encontrada"),
        403: OpenApiResponse(description="Permisos insuficientes"),
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsModerator])
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    serializer = CategoriaSerializer(categoria, data=request.data)
    if serializer.is_valid():
        categoria = serializer.save()
        return Response(CategoriaSerializer(categoria).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# DELETE /categorias/{pk}/delete/ — Eliminar categoría
# ============================================================
@extend_schema(
    summary="Eliminar categoría",
    description="Elimina una categoría en base a su ID. Solo para moderadores.",
    tags=["Categorías"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la categoría a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Categoría eliminada"),
        404: OpenApiResponse(description="Categoría no encontrada"),
        403: OpenApiResponse(description="Permisos insuficientes"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsModerator])
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# POST /categorias/{pk}/toggle-estado/ — Alternar estado activo
# ============================================================
@extend_schema(
    summary="Alternar estado activo/inactivo",
    description="Cambia el estado del campo `activo` de la categoría seleccionada.",
    tags=["Categorías"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la categoría cuyo estado cambiar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=CategoriaSerializer),
        404: OpenApiResponse(description="Categoría no encontrada"),
        403: OpenApiResponse(description="Permisos insuficientes"),
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsModerator])
def categoria_toggle_estado(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.activo = not categoria.activo
    categoria.save()
    return Response(CategoriaSerializer(categoria).data, status=status.HTTP_200_OK)