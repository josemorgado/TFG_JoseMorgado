from ast import IsNot
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import IsAnonymousOrModerator, IsAuthorOrModerator, IsModerator, IsAnonymousUser
from rest_framework.decorators import (
    api_view, parser_classes, permission_classes, authentication_classes
)
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from .serializers import UserLiteSerializer, UserPerfilSerializer
from .models import Perfil

User = get_user_model()


# ============================================================
# GET /usuarios/ — Listar usuarios
# ============================================================
@extend_schema(
    summary="Listar usuarios",
    description="Devuelve todos los usuarios registrados junto con su perfil asociado.",
    tags=["Usuarios"],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def usuario_list(request):
    qs = User.objects.select_related('perfil').all().order_by('id')
    serializer = UserPerfilSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# GET /usuarios/{pk}/ — Detalle usuario + perfil
# ============================================================
@extend_schema(
    summary="Obtener detalle de un usuario",
    description="Devuelve la información completa de un usuario y su perfil.",
    tags=["Usuarios"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del usuario",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer),
        404: OpenApiResponse(description="Usuario no encontrado"),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def usuario_detail(request, pk):
    user = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
    serializer = UserPerfilSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# POST /usuarios/create/ — Crear usuario + perfil
# ============================================================
@extend_schema(
    summary="Crear usuario",
    description=(
        "Crea un nuevo usuario junto con su perfil. "
        "Soporta multipart/form-data para subir foto de perfil."
    ),
    tags=["Usuarios"],
    request=UserPerfilSerializer,
    responses={
        201: OpenApiResponse(response=UserPerfilSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo creación",
            value={
                "username": "juan123",
                "email": "juan@example.com",
                "password": "MiPass1234",
                "telefono": "666777888",
                "bio": "Vecino del distrito centro"
            },
            request_only=True
        )
    ]
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAnonymousOrModerator])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_create(request):
    serializer = UserPerfilSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    user = User.objects.select_related('perfil').get(pk=user.pk)

    return Response(
        UserPerfilSerializer(user, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


# ============================================================
# PUT /usuarios/{pk}/update/ — Update completo
# ============================================================
@extend_schema(
    summary="Actualizar usuario (completo)",
    description="Actualiza todos los campos de un usuario y su perfil asociado.",
    tags=["Usuarios"],
    request=UserPerfilSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del usuario a actualizar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Usuario no encontrado"),
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_update(request, pk):
    # ---- Early 403: si no es moderador y no es su propio pk, corta aquí
    is_moderator = getattr(getattr(request.user, 'perfil', None), 'moderator', False)
    try:
        target_pk = int(pk)
    except (TypeError, ValueError):
        return Response({"detail": "Parámetro pk inválido."}, status=status.HTTP_400_BAD_REQUEST)

    if not is_moderator and request.user.id != target_pk:
        return Response({"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN)

    # ---- A partir de aquí, ya puede buscar el objeto
    user = get_object_or_404(User.objects.select_related('perfil'), pk=pk)

    # Check de objeto (por consistencia y seguridad)
    perm = IsAuthorOrModerator()
    if not perm.has_object_permission(request, None, user):
        return Response({"detail": perm.message}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserPerfilSerializer(user, data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user = User.objects.select_related('perfil').get(pk=user.pk)
    return Response(UserPerfilSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)


# ============================================================
# PATCH /usuarios/{pk}/partial-update/ — Update parcial
# ============================================================
@extend_schema(
    summary="Actualizar usuario (parcial)",
    description="Actualiza parcialmente los datos de un usuario y su perfil.",
    tags=["Usuarios"],
    request=UserPerfilSerializer,
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del usuario a actualizar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Usuario no encontrado"),
    }
)
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_partial_update(request, pk):
    is_moderator = getattr(getattr(request.user, 'perfil', None), 'moderator', False)
    try:
        target_pk = int(pk)
    except (TypeError, ValueError):
        return Response({"detail": "Parámetro pk inválido."}, status=status.HTTP_400_BAD_REQUEST)

    if not is_moderator and request.user.id != target_pk:
        return Response({"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User.objects.select_related('perfil'), pk=pk)

    perm = IsAuthorOrModerator()
    if not perm.has_object_permission(request, None, user):
        return Response({"detail": perm.message}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserPerfilSerializer(user, data=request.data, partial=True, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user = User.objects.select_related('perfil').get(pk=user.pk)
    return Response(UserPerfilSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)


# ============================================================
# DELETE /usuarios/{pk}/delete/ — Eliminar usuario
# ============================================================
@extend_schema(
    summary="Eliminar usuario",
    description="Elimina un usuario junto con su perfil asociado. Solo autor o moderador.",
    tags=["Usuarios"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del usuario a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="Usuario eliminado"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Usuario no encontrado"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def usuario_delete(request, pk):
    is_moderator = getattr(getattr(request.user, 'perfil', None), 'moderator', False)
    try:
        target_pk = int(pk)
    except (TypeError, ValueError):
        return Response({"detail": "Parámetro pk inválido."}, status=status.HTTP_400_BAD_REQUEST)

    if not is_moderator and request.user.id != target_pk:
        return Response({"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, pk=pk)

    perm = IsAuthorOrModerator()
    if not perm.has_object_permission(request, None, user):
        return Response({"detail": perm.message}, status=status.HTTP_403_FORBIDDEN)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# GET/PATCH/PUT /usuarios/me/ → Permite al usuario autenticado leer/actualizar su propio perfil
@api_view(['GET', 'PATCH', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])  # Solo el propio usuario o moderadores pueden acceder a esta vista
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_me(request):
    # Carga el user con su perfil para evitar N+1
    user = User.objects.select_related('perfil').get(pk=request.user.pk)

    if request.method == 'GET':
        serializer = UserPerfilSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    partial = (request.method == 'PATCH')
    serializer = UserPerfilSerializer(
        instance=user,
        data=request.data,
        partial=partial,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    # Recarga para asegurar consistencia y perfil actualizado
    user = User.objects.select_related('perfil').get(pk=request.user.pk)
    return Response(UserPerfilSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)