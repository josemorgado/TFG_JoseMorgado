from rest_framework.decorators import api_view, parser_classes, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from core.permissions import IsAuthorOrModerator
from .models import Imagen
from .serializers import ImagenSerializer


# ============================================================
# GET /imagenes/ — Listado de imágenes
# ============================================================
@extend_schema(
    summary="Listar imágenes",
    description="Devuelve todas las imágenes almacenadas, ordenadas por su ID.",
    tags=["Imágenes"],
    responses={
        200: OpenApiResponse(response=ImagenSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def imagen_list(request):
    qs = Imagen.objects.all().order_by('id')
    serializer = ImagenSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /imagenes/{pk}/ — Detalle de una imagen
# ============================================================
@extend_schema(
    summary="Obtener detalle de una imagen",
    description="Retorna la información completa de una imagen según su ID.",
    tags=["Imágenes"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la imagen a consultar",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=ImagenSerializer),
        404: OpenApiResponse(description="Imagen no encontrada"),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def imagen_detail(request, pk):
    imagen = get_object_or_404(Imagen, pk=pk)
    serializer = ImagenSerializer(imagen)
    return Response(serializer.data)


# ============================================================
# GET /imagenes/queja/{queja_id}/ — Imágenes asociadas a una queja
# ============================================================
@extend_schema(
    summary="Listar imágenes de una queja",
    description="Devuelve todas las imágenes asociadas a una queja concreta, ordenadas por el campo 'orden'.",
    tags=["Imágenes"],
    parameters=[
        OpenApiParameter(
            name="queja_id",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=ImagenSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def imagenes_por_queja(request, queja_id):
    queja_ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = Imagen.objects.filter(content_type=queja_ct, object_id=queja_id).order_by('orden')
    serializer = ImagenSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /imagenes/comentario/{comentario_id}/ — Imágenes asociadas a un comentario
# ============================================================
@extend_schema(
    summary="Listar imágenes de un comentario",
    description="Devuelve todas las imágenes asociadas a un comentario, ordenadas por el campo 'orden'.",
    tags=["Imágenes"],
    parameters=[
        OpenApiParameter(
            name="comentario_id",
            type=int,
            description="ID del comentario",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=ImagenSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def imagenes_por_comentario(request, comentario_id):
    comentario_ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = Imagen.objects.filter(content_type=comentario_ct, object_id=comentario_id).order_by('orden')
    serializer = ImagenSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# POST /imagenes/create/ — Subir una imagen (multipart)
# ============================================================
@extend_schema(
    summary="Subir imagen",
    description=(
        "Crea una nueva imagen asociada a una queja o comentario. "
        "El archivo se envía mediante multipart/form-data."
    ),
    tags=["Imágenes"],
    request=ImagenSerializer,
    responses={
        201: OpenApiResponse(response=ImagenSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de creación",
            value={
                "file": "(archivo binario)",
                "content_type": "quejas.queja",
                "object_id": 15
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def imagen_create(request):
    serializer = ImagenSerializer(data=request.data)

    if serializer.is_valid():
        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']

        qs = Imagen.objects.filter(content_type=content_type, object_id=object_id)

        nuevo_orden = qs.order_by('-orden').first().orden + 1 if qs.exists() else 0

        imagen = serializer.save(orden=nuevo_orden)
        return Response(ImagenSerializer(imagen).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# DELETE /imagenes/{pk}/delete/ — Eliminar imagen
# ============================================================
@extend_schema(
    summary="Eliminar imagen",
    description="Elimina una imagen según su ID. Requiere ser autor o moderador.",
    tags=["Imágenes"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID de la imagen a eliminar",
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        204: OpenApiResponse(description="Imagen eliminada"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Imagen no encontrada"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def imagen_delete(request, pk):
    imagen = get_object_or_404(Imagen, pk=pk)
    imagen.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)