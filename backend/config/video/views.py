from rest_framework.decorators import api_view, parser_classes, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import IsAuthorOrModerator, IsModeratorOrRelatedQuejaAuthor
from .models import Video
from .serializers import VideoSerializer

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)


# ============================================================
# GET /videos/ — Listado general
# ============================================================
@extend_schema(
    summary="Listar videos",
    description="Devuelve todos los videos almacenados, ordenados por ID ascendente.",
    tags=["Videos"],
    responses={
        200: OpenApiResponse(response=VideoSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])  # Cualquiera puede acceder
def video_list(request):
    qs = Video.objects.all().order_by('id')
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /videos/{pk}/ — Detalle de un video
# ============================================================
@extend_schema(
    summary="Obtener detalle de un video",
    description="Retorna la información completa de un video según su ID.",
    tags=["Videos"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del video",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=VideoSerializer),
        404: OpenApiResponse(description="Video no encontrado"),
    }
)
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([AllowAny])
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    serializer = VideoSerializer(video)
    return Response(serializer.data)


# ============================================================
# GET /videos/queja/{queja_id}/ — Videos por queja
# ============================================================
@extend_schema(
    summary="Listar videos de una queja",
    description="Devuelve los videos asociados a una queja, ordenados por su campo `orden`.",
    tags=["Videos"],
    parameters=[
        OpenApiParameter(
            name="queja_id",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={200: OpenApiResponse(response=VideoSerializer(many=True))}
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def videos_por_queja(request, queja_id):
    queja_ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = Video.objects.filter(content_type=queja_ct, object_id=queja_id).order_by('orden')
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /videos/comentario/{comentario_id}/ — Videos por comentario
# ============================================================
@extend_schema(
    summary="Listar videos de un comentario",
    description="Devuelve los videos asociados a un comentario, ordenados por su campo `orden`.",
    tags=["Videos"],
    parameters=[
        OpenApiParameter(
            name="comentario_id",
            type=int,
            description="ID del comentario",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={200: OpenApiResponse(response=VideoSerializer(many=True))}
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def videos_por_comentario(request, comentario_id):
    comentario_ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = Video.objects.filter(content_type=comentario_ct, object_id=comentario_id).order_by('orden')
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# POST /videos/create/ — Subir video (multipart)
# ============================================================
@extend_schema(
    summary="Subir video",
    description="Sube un nuevo video asociado a una queja o comentario. El archivo debe enviarse en multipart/form-data.",
    tags=["Videos"],
    request=VideoSerializer,
    responses={
        201: OpenApiResponse(response=VideoSerializer),
        400: OpenApiResponse(description="Datos inválidos o límite de videos alcanzado"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo creación",
            value={
                "file": "(archivo de video)",
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
def video_create(request):
    serializer = VideoSerializer(data=request.data)

    if serializer.is_valid():
        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']

        qs = Video.objects.filter(content_type=content_type, object_id=object_id)

        if qs.exists():
            ultimo = qs.order_by('-orden').first()
            nuevo_orden = ultimo.orden + 1
        else:
            nuevo_orden = 0

        try:
            video = serializer.save(orden=nuevo_orden)
        except DjangoValidationError as e:
            payload = {'detail': e.message_dict if hasattr(e, 'message_dict') else e.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# DELETE /videos/{pk}/delete/ — Eliminar video
# ============================================================
@extend_schema(
    summary="Eliminar video",
    description="Elimina un video por su ID. Se requiere ser autor o moderador.",
    tags=["Videos"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del video a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Video eliminado"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Video no encontrado"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsModeratorOrRelatedQuejaAuthor])
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    permission = IsModeratorOrRelatedQuejaAuthor()
    if not permission.has_object_permission(request, None, video):
        return Response({'detail': 'No tienes permiso para eliminar este video.'}, status=status.HTTP_403_FORBIDDEN)
    video.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)