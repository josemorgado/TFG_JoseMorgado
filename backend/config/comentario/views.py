from multiprocessing import context

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from core.permissions import IsAuthorOrModerator, IsModerator
from comentario.models import Comentario
from comentario.serializers import ComentarioSerializer


# ============================================================
# GET /comentario/ — Listado de comentarios ordenados por fecha
# ============================================================
@extend_schema(
    summary="Listar comentarios",
    description="Devuelve el listado de comentarios ordenado por fecha de creación ascendente.",
    tags=["Comentarios"],
    responses={
        200: OpenApiResponse(response=ComentarioSerializer(many=True)),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def comentario_list(request):
    qs = Comentario.objects.all().order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


# ============================================================
# GET /comentario/{pk}/ — Detalle de un comentario por ID
# ============================================================
@extend_schema(
    summary="Obtener detalle de un comentario",
    description="Retorna los datos completos de un comentario según su ID.",
    tags=["Comentarios"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del comentario a consultar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=ComentarioSerializer),
        404: OpenApiResponse(description="Comentario no encontrado"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def comentario_detail(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    serializer = ComentarioSerializer(comentario, context={'request': request})
    return Response(serializer.data)


# ============================================================
# GET /comentario/queja/{queja_id}/ — Comentarios por queja
# ============================================================
@extend_schema(
    summary="Listar comentarios de una queja",
    description="Devuelve los comentarios asociados a una queja concreta, ordenados por fecha de creación.",
    tags=["Comentarios"],
    parameters=[
        OpenApiParameter(
            name="queja_id",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=ComentarioSerializer(many=True)),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def comentarios_por_queja(request, queja_id):
    qs = Comentario.objects.filter(queja_id=queja_id).order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


# ============================================================
# GET /comentario/user/{user_id}/ — Comentarios por usuario
# ============================================================
@extend_schema(
    summary="Listar comentarios de un usuario",
    description="Devuelve los comentarios realizados por un usuario concreto, ordenados por fecha de creación.",
    tags=["Comentarios"],
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            description="ID del usuario autor",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=ComentarioSerializer(many=True)),
        404: OpenApiResponse(description="Usuario no encontrado"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def comentarios_por_usuario(request, user_id):
    get_object_or_404(User, pk=user_id)
    qs = Comentario.objects.filter(autor_id=user_id).order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


# ============================================================
# POST /comentario/create/ — Crear comentario
# ============================================================
@extend_schema(
    summary="Crear comentario",
    description="Crea un nuevo comentario. Requiere autenticación JWT.",
    tags=["Comentarios"],
    request=ComentarioSerializer,
    responses={
        201: OpenApiResponse(response=ComentarioSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de request",
            value={
                "queja": 12,
                "contenido": "Totalmente de acuerdo con esta queja.",
            },
            request_only=True
        ),
        OpenApiExample(
            "Ejemplo de response (201)",
            value={
                "id": 101,
                "queja": 12,
                "autor": 5,
                "contenido": "Totalmente de acuerdo con esta queja.",
                "fecha_creacion": "2026-02-16T10:30:00Z"
            },
            response_only=True
        ),
    ]
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def comentario_create(request):
    serializer = ComentarioSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        comentario = serializer.save(autor=request.user)
        return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# PUT /comentario/{pk}/update/ — Actualización completa
# ============================================================
@extend_schema(
    summary="Actualizar comentario",
    description="Actualiza completamente un comentario existente. Requiere ser autor o moderador.",
    tags=["Comentarios"],
    request=ComentarioSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del comentario a actualizar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=ComentarioSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes (no autor/moderador)"),
        404: OpenApiResponse(description="Comentario no encontrado"),
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def comentario_update(request, pk):
    # 1) Carga el comentario
    comentario = get_object_or_404(Comentario, pk=pk)

    # 2) Calcula si el usuario es moderador
    is_moderator = getattr(getattr(request.user, 'perfil', None), 'moderator', False)

    # 3) Chequeo de permisos a nivel de objeto:
    #    - Si NO es moderador y NO es el autor del comentario -> 403
    if not is_moderator and comentario.autor_id != request.user.id:
        return Response({"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN)

    # 4) Serializar con contexto
    serializer = ComentarioSerializer(
        comentario,
        data=request.data,
        context={"request": request}
    )

    if serializer.is_valid():
        comentario = serializer.save()
        return Response(ComentarioSerializer(comentario).data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# DELETE /comentario/{pk}/delete/ — Eliminar comentario
# ============================================================
@extend_schema(
    summary="Eliminar comentario",
    description="Elimina un comentario por su ID. Requiere ser autor o moderador.",
    tags=["Comentarios"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del comentario a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Comentario eliminado"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes (no autor/moderador)"),
        404: OpenApiResponse(description="Comentario no encontrado"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def comentario_delete(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    # 1) Carga el comentario
    comentario = get_object_or_404(Comentario, pk=pk)

    # 2) Calcula si el usuario es moderador
    is_moderator = getattr(getattr(request.user, 'perfil', None), 'moderator', False)

    # 3) Chequeo de permisos a nivel de objeto:
    #    - Si NO es moderador y NO es el autor del comentario -> 403
    if not is_moderator and comentario.autor_id != request.user.id:
        return Response({"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN)

    comentario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
