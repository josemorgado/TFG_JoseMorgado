# quejas/views.py
from re import U
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import IsModerator, IsAuthorOrModerator
from quejas.serializers import QuejaSerializer
from quejas.models import Queja
from django.contrib.auth import get_user_model

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

User = get_user_model()

# GET /quejas/ → Lista todas las quejas
@extend_schema(
    summary="Listar quejas",
    description="Devuelve el listado completo de quejas ordenadas por ID ascendente.",
    tags=["Quejas"],
    responses={
        200: OpenApiResponse(response=QuejaSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])  # Cualquiera puede acceder
def quejas_list(request):
    qs = Queja.objects.all().order_by('id')
    serializer = QuejaSerializer(qs, many=True)  # salida: no hace falta context
    return Response(serializer.data)


# GET /quejas/<int:pk>/ → Detalle de una queja
@extend_schema(
    summary="Obtener detalle de una queja",
    description="Retorna los datos completos de una queja a partir de su ID.",
    tags=["Quejas"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=QuejaSerializer),
        404: OpenApiResponse(description="Queja no encontrada"),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])  # Cualquiera puede acceder
def queja_detail(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    serializer = QuejaSerializer(queja)  # salida: no hace falta context
    return Response(serializer.data)


# GET /quejas/categoria/<int:categoria_id>/ → Lista quejas filtradas por categoría
@extend_schema(
    summary="Listar quejas por categoría",
    description="Devuelve las quejas asociadas a una categoría concreta.",
    tags=["Quejas"],
    parameters=[
        OpenApiParameter(
            name="categoria_id",
            type=int,
            description="ID de la categoría",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=QuejaSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])  # Cualquiera puede acceder
def quejas_por_categoria(request, categoria_id):
    qs = Queja.objects.filter(categoria_id=categoria_id).order_by('id')
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /quejas/distrito/<int:distrito_id>/ → Lista quejas filtradas por distrito
@extend_schema(
    summary="Listar quejas por distrito",
    description="Devuelve las quejas asociadas a un distrito concreto.",
    tags=["Quejas"],
    parameters=[
        OpenApiParameter(
            name="distrito_id",
            type=int,
            description="ID del distrito",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=QuejaSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])  # Cualquiera puede acceder
def quejas_por_distrito(request, distrito_id):
    qs = Queja.objects.filter(distrito_id=distrito_id).order_by('id')
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)


# POST /quejas/create/ → Crea una queja nueva (valida con serializer)
@extend_schema(
    summary="Crear queja",
    description="Crea una nueva queja utilizando el serializer para validación.",
    tags=["Quejas"],
    request=QuejaSerializer,
    responses={
        201: OpenApiResponse(response=QuejaSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de creación",
            value={
                "titulo": "Acera en mal estado",
                "descripcion": "Hay losas sueltas en la calle Mayor.",
                "categoria": 3,
                "distrito": 1
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Solo usuarios autenticados pueden crear quejas
def queja_create(request):
    # El serializer usa request en create/validate → pasar context
    serializer = QuejaSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        queja = serializer.save()
        return Response(QuejaSerializer(queja).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /quejas/<int:pk>/update/ → Reemplaza completamente una queja
@extend_schema(
    summary="Actualizar queja (completo)",
    description="Actualiza completamente los datos de una queja existente.",
    tags=["Quejas"],
    request=QuejaSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=QuejaSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Queja no encontrada"),
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])  # Solo usuarios autenticados pueden actualizar quejas
def queja_update(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    # PUT = actualización total → partial=False
    serializer = QuejaSerializer(queja, data=request.data, context={'request': request})
    if serializer.is_valid():
        queja = serializer.save()
        return Response(QuejaSerializer(queja).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /quejas/<int:pk>/delete/ → Elimina una queja por su identificador
@extend_schema(
    summary="Eliminar queja",
    description="Elimina una queja por su ID.",
    tags=["Quejas"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Queja eliminada"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Queja no encontrada"),
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # Solo usuarios autenticados pueden eliminar quejas
def queja_delete(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    queja.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# GET /quejas/autor/<int:autor_id>/ → Lista quejas creadas por un usuario (autor)
@extend_schema(
    summary="Listar quejas por autor",
    description="Devuelve las quejas creadas por un usuario concreto.",
    tags=["Quejas"],
    parameters=[
        OpenApiParameter(
            name="autor_id",
            type=int,
            description="ID del usuario autor de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=QuejaSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])  # Cualquiera puede acceder
def quejas_por_autor(request, autor_id):
    qs = Queja.objects.filter(autor_id=autor_id).order_by('id')
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)


# PATCH /quejas/<int:pk>/estado/ → Cambia SOLO el estado de la queja
@extend_schema(
    summary="Cambiar estado de la queja",
    description=(
        "Cambia únicamente el campo `estado` de la queja. "
        "Valores permitidos según choices del modelo (p. ej.: 'PEN', 'ENP', 'RES', 'REC')."
    ),
    tags=["Quejas"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la queja a modificar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    request=None,  # se envía un body JSON simple con {'estado': '<valor>'}
    responses={
        200: OpenApiResponse(response=QuejaSerializer, description="Estado actualizado"),
        400: OpenApiResponse(description="Solicitud inválida o estado no permitido"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes (solo moderadores)"),
        404: OpenApiResponse(description="Queja no encontrada"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo body",
            value={"estado": "ENP"},
            request_only=True
        )
    ]
)
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])  # Autenticación JWT
@permission_classes([IsAuthenticated, IsModerator])  # Solo moderadores pueden cambiar el estado de las quejas
def queja_cambiar_estado(request, pk):
    # Espera un body JSON con {"estado": "PEN" | "ENP" | "RES" | "REC"}
    queja = get_object_or_404(Queja, pk=pk)

    # Solo permitimos cambiar el 'estado'
    estado = request.data.get('estado')
    if estado is None:
        return Response({"estado": ["Este campo es requerido."]}, status=status.HTTP_400_BAD_REQUEST)

    # Validación básica contra choices del modelo
    valid_values = {choice[0] for choice in queja._meta.get_field('estado').choices}
    if estado not in valid_values:
        return Response(
            {"estado": [f"Valor inválido. Debe ser uno de {sorted(valid_values)}"]},
            status=status.HTTP_400_BAD_REQUEST
        )

    queja.estado = estado
    queja.save(update_fields=['estado', 'fecha_actualizacion'])
    return Response(QuejaSerializer(queja).data, status=status.HTTP_200_OK)