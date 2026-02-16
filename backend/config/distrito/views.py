from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from core.permissions import IsAuthorOrModerator
from distrito.models import Distrito
from distrito.serializers import DistritoSerializer


# ============================================================
# GET /distritos/ — Listado de distritos
# ============================================================
@extend_schema(
    summary="Listar distritos",
    description="Devuelve el listado de distritos ordenados por su ID.",
    tags=["Distritos"],
    responses={
        200: OpenApiResponse(response=DistritoSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def distrito_list(request):
    qs = Distrito.objects.all().order_by('id')
    serializer = DistritoSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /distritos/{pk}/ — Detalle de un distrito
# ============================================================
@extend_schema(
    summary="Obtener detalle de un distrito",
    description="Retorna los datos completos de un distrito según su ID.",
    tags=["Distritos"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del distrito a consultar",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=DistritoSerializer),
        404: OpenApiResponse(description="Distrito no encontrado"),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def distrito_detail(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    serializer = DistritoSerializer(distrito)
    return Response(serializer.data)


# ============================================================
# POST /distritos/create/ — Crear distrito
# ============================================================
@extend_schema(
    summary="Crear distrito",
    description="Crea un nuevo distrito. Requiere autenticación mediante JWT.",
    tags=["Distritos"],
    request=DistritoSerializer,
    responses={
        201: OpenApiResponse(response=DistritoSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de request",
            value={"nombre": "Distrito Centro", "codigo": "DC001"},
            request_only=True
        )
    ]
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def distrito_create(request):
    serializer = DistritoSerializer(data=request.data)
    if serializer.is_valid():
        distrito = serializer.save()
        return Response(DistritoSerializer(distrito).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# PUT /distritos/{pk}/update/ — Actualizar un distrito
# ============================================================
@extend_schema(
    summary="Actualizar distrito",
    description="Actualiza completamente un distrito. Requiere ser autor o moderador.",
    tags=["Distritos"],
    request=DistritoSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del distrito a actualizar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=DistritoSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Distrito no encontrado"),
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def distrito_update(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    serializer = DistritoSerializer(distrito, data=request.data)
    if serializer.is_valid():
        distrito = serializer.save()
        return Response(DistritoSerializer(distrito).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# DELETE /distritos/{pk}/delete/ — Eliminar un distrito
# ============================================================
@extend_schema(
    summary="Eliminar distrito",
    description="Elimina un distrito por su ID. Requiere ser autor o moderador.",
    tags=["Distritos"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del distrito a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Distrito eliminado"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Distrito no encontrado"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def distrito_delete(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    distrito.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)