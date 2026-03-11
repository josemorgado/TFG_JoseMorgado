from ast import IsNot
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from video.serializers import VideoSerializer
from video.models import Video
from core.permissions import (
    IsAnonymousOrModerator,
    IsAuthorOrModerator,
    IsModerator,
    IsAnonymousUser,
)
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
    authentication_classes,
)

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from imagen.serializers import ImagenSerializer
from imagen.models import Imagen
from quejas.models import Queja
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)

from .serializers import UserPerfilSerializer, UserWithPerfilSerializer
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
    },
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def usuario_list(request):
    qs = User.objects.select_related("perfil").all().order_by("id")
    serializer = UserPerfilSerializer(qs, many=True, context={"request": request})
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
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer),
        404: OpenApiResponse(description="Usuario no encontrado"),
    },
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def usuario_detail(request, pk):
    user = get_object_or_404(User.objects.select_related("perfil"), pk=pk)
    serializer = UserWithPerfilSerializer(user, context={"request": request})
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
                "bio": "Vecino del distrito centro",
            },
            request_only=True,
        )
    ],
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAnonymousOrModerator])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_create(request):
    serializer = UserPerfilSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    user = User.objects.select_related("perfil").get(pk=user.pk)

    return Response(
        UserPerfilSerializer(user, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
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
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Usuario no encontrado"),
    },
)
@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_update(request, pk):
    # ---- Early 403: si no es moderador y no es su propio pk, corta aquí
    is_moderator = getattr(getattr(request.user, "perfil", None), "moderator", False)
    try:
        target_pk = int(pk)
    except (TypeError, ValueError):
        return Response(
            {"detail": "Parámetro pk inválido."}, status=status.HTTP_400_BAD_REQUEST
        )

    if not is_moderator and request.user.id != target_pk:
        return Response(
            {"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN
        )

    # ---- A partir de aquí, ya puede buscar el objeto
    user = get_object_or_404(User.objects.select_related("perfil"), pk=pk)

    # Check de objeto (por consistencia y seguridad)
    perm = IsAuthorOrModerator()
    if not perm.has_object_permission(request, None, user):
        return Response({"detail": perm.message}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserPerfilSerializer(
        user, data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user = User.objects.select_related("perfil").get(pk=user.pk)
    return Response(
        UserPerfilSerializer(user, context={"request": request}).data,
        status=status.HTTP_200_OK,
    )


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
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(response=UserPerfilSerializer),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Usuario no encontrado"),
    },
)
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_partial_update(request, pk):
    is_moderator = getattr(getattr(request.user, "perfil", None), "moderator", False)
    try:
        target_pk = int(pk)
    except (TypeError, ValueError):
        return Response(
            {"detail": "Parámetro pk inválido."}, status=status.HTTP_400_BAD_REQUEST
        )

    if not is_moderator and request.user.id != target_pk:
        return Response(
            {"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN
        )

    user = get_object_or_404(User.objects.select_related("perfil"), pk=pk)

    perm = IsAuthorOrModerator()
    if not perm.has_object_permission(request, None, user):
        return Response({"detail": perm.message}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserPerfilSerializer(
        user, data=request.data, partial=True, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user = User.objects.select_related("perfil").get(pk=user.pk)
    return Response(
        UserPerfilSerializer(user, context={"request": request}).data,
        status=status.HTTP_200_OK,
    )


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
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        204: OpenApiResponse(description="Usuario eliminado"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="Usuario no encontrado"),
    },
)
@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def usuario_delete(request, pk):
    is_moderator = getattr(getattr(request.user, "perfil", None), "moderator", False)
    try:
        target_pk = int(pk)
    except (TypeError, ValueError):
        return Response(
            {"detail": "Parámetro pk inválido."}, status=status.HTTP_400_BAD_REQUEST
        )

    if not is_moderator and request.user.id != target_pk:
        return Response(
            {"detail": IsAuthorOrModerator.message}, status=status.HTTP_403_FORBIDDEN
        )

    user = get_object_or_404(User, pk=pk)

    perm = IsAuthorOrModerator()
    if not perm.has_object_permission(request, None, user):
        return Response({"detail": perm.message}, status=status.HTTP_403_FORBIDDEN)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# GET/PATCH/PUT /usuarios/me/ → Permite al usuario autenticado leer/actualizar su propio perfil
@api_view(["GET", "PATCH", "PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes(
    [IsAuthenticated]
)  # Solo el propio usuario o moderadores pueden acceder a esta vista
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_me(request):
    # Carga el user con su perfil para evitar N+1
    user = User.objects.select_related("perfil").get(pk=request.user.pk)

    if request.method == "GET":
        serializer = UserPerfilSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    partial = request.method == "PATCH"
    serializer = UserPerfilSerializer(
        instance=user, data=request.data, partial=partial, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    # Recarga para asegurar consistencia y perfil actualizado
    user = User.objects.select_related("perfil").get(pk=request.user.pk)
    return Response(
        UserPerfilSerializer(user, context={"request": request}).data,
        status=status.HTTP_200_OK,
    )


# ============================================================
# GET /usuarios/{user_id}/imagenes — Todas las imágenes de las quejas de un usuario
# ============================================================
@extend_schema(
    summary="Listar imágenes de un usuario (por sus quejas)",
    description=(
        "Devuelve todas las imágenes asociadas a las quejas creadas por el usuario indicado. "
        "Usa ContentType de Queja + object_id de cada queja del usuario."
    ),
    tags=["Imágenes"],
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            description="ID del usuario autor de las quejas",
            required=True,
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name="page",
            type=int,
            description="Número de página (opcional, paginación simple)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description="Tamaño de página (opcional, por defecto 20, máximo 100)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(response=ImagenSerializer(many=True)),
        404: OpenApiResponse(
            description="Usuario sin quejas o inexistente (si aplicas verificación previa)"
        ),
    },
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def imagenes_de_usuario(request, user_id: int):
    """
    Retorna todas las imágenes de las quejas cuyo autor sea `user_id`.
    Orden: orden -> fecha_creacion -> id
    Paginación simple por query params.
    """
    user = get_object_or_404(
        User, pk=user_id
    )  # Verifica que el usuario existe, si no devuelve 404
    # 1) Obtener ids de quejas del usuario
    queja_ids = list(
        Queja.objects.filter(autor_id=user_id).values_list("id", flat=True)
    )
    if not queja_ids:
        return Response([], status=status.HTTP_200_OK)

    # 2) Filtrar Imagen por ContentType de Queja + object_id in ids
    queja_ct = ContentType.objects.get_for_model(Queja, for_concrete_model=False)

    qs = Imagen.objects.filter(content_type=queja_ct, object_id__in=queja_ids).order_by(
        "orden", "fecha_creacion", "id"
    )

    # --- Paginación simple
    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 20)), 100)
    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = []

    serializer = ImagenSerializer(page_obj, many=True, context={"request": request})

    return Response(
        {
            "count": paginator.count if hasattr(paginator, "count") else len(qs),
            "page": page,
            "page_size": page_size,
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# GET /usuarios/me/imagenes — Imágenes de mis quejas (del usuario autenticado)
# ============================================================
@extend_schema(
    summary="Listar imágenes de mis quejas",
    description="Devuelve todas las imágenes asociadas a las quejas creadas por el usuario autenticado.",
    tags=["Imágenes"],
    parameters=[
        OpenApiParameter(
            name="page",
            type=int,
            description="Número de página (opcional, paginación simple)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description="Tamaño de página (opcional, por defecto 20, máximo 100)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(response=ImagenSerializer(many=True)),
        401: OpenApiResponse(description="No autenticado"),
    },
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mis_imagenes(request):
    """
    Retorna todas las imágenes de las quejas cuyo autor es el usuario autenticado.
    Orden: orden -> fecha_creacion -> id
    Paginación simple por query params.
    """
    user_id = request.user.id

    queja_ids = list(
        Queja.objects.filter(autor_id=user_id).values_list("id", flat=True)
    )
    if not queja_ids:
        return Response([], status=status.HTTP_200_OK)

    queja_ct = ContentType.objects.get_for_model(Queja, for_concrete_model=False)

    qs = Imagen.objects.filter(content_type=queja_ct, object_id__in=queja_ids).order_by(
        "orden", "fecha_creacion", "id"
    )

    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 20)), 100)
    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = []

    serializer = ImagenSerializer(page_obj, many=True, context={"request": request})

    return Response(
        {
            "count": paginator.count if hasattr(paginator, "count") else len(qs),
            "page": page,
            "page_size": page_size,
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# GET /usuarios/{user_id}/videos — Todos las videos de las quejas de un usuario
# ============================================================
@extend_schema(
    summary="Listar videos de un usuario (por sus quejas)",
    description=(
        "Devuelve todos los videos asociados a las quejas creadas por el usuario indicado. "
        "Usa ContentType de Queja + object_id de cada queja del usuario."
    ),
    tags=["Videos"],
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            description="ID del usuario autor de las quejas",
            required=True,
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name="page",
            type=int,
            description="Número de página (opcional, paginación simple)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description="Tamaño de página (opcional, por defecto 20, máximo 100)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(response=VideoSerializer(many=True)),
        404: OpenApiResponse(
            description="Usuario sin quejas o inexistente (si aplicas verificación previa)"
        ),
    },
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def videos_de_usuario(request, user_id: int):
    """
    Retorna todos los videos de las quejas cuyo autor sea `user_id`.
    Orden: orden -> fecha_creacion -> id
    Paginación simple por query params.
    """
    user = get_object_or_404(
        User, pk=user_id
    )  # Verifica que el usuario existe, si no devuelve 404
    # 1) Obtener ids de quejas del usuario
    queja_ids = list(
        Queja.objects.filter(autor_id=user_id).values_list("id", flat=True)
    )
    if not queja_ids:
        return Response([], status=status.HTTP_200_OK)

    # 2) Filtrar Video por ContentType de Queja + object_id in ids
    queja_ct = ContentType.objects.get_for_model(Queja, for_concrete_model=False)

    qs = Video.objects.filter(content_type=queja_ct, object_id__in=queja_ids).order_by(
        "orden", "fecha_creacion", "id"
    )

    # --- Paginación simple
    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 20)), 100)
    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = []

    serializer = VideoSerializer(page_obj, many=True, context={"request": request})

    return Response(
        {
            "count": paginator.count if hasattr(paginator, "count") else len(qs),
            "page": page,
            "page_size": page_size,
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# GET /usuarios/me/videos — Videos de mis quejas (del usuario autenticado)
# ============================================================
@extend_schema(
    summary="Listar videos de mis quejas",
    description="Devuelve todos los videos asociados a las quejas creadas por el usuario autenticado.",
    tags=["Videos"],
    parameters=[
        OpenApiParameter(
            name="page",
            type=int,
            description="Número de página (opcional, paginación simple)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            description="Tamaño de página (opcional, por defecto 20, máximo 100)",
            required=False,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(response=VideoSerializer(many=True)),
        401: OpenApiResponse(description="No autenticado"),
    },
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mis_videos(request):
    """
    Retorna todos los videos de las quejas cuyo autor es el usuario autenticado.
    Orden: orden -> fecha_creacion -> id
    Paginación simple por query params.
    """
    user_id = request.user.id

    queja_ids = list(
        Queja.objects.filter(autor_id=user_id).values_list("id", flat=True)
    )
    if not queja_ids:
        return Response([], status=status.HTTP_200_OK)

    queja_ct = ContentType.objects.get_for_model(Queja, for_concrete_model=False)

    qs = Video.objects.filter(content_type=queja_ct, object_id__in=queja_ids).order_by(
        "orden", "fecha_creacion", "id"
    )

    page = int(request.query_params.get("page", 1))
    page_size = min(int(request.query_params.get("page_size", 20)), 100)
    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = []

    serializer = VideoSerializer(page_obj, many=True, context={"request": request})

    return Response(
        {
            "count": paginator.count if hasattr(paginator, "count") else len(qs),
            "page": page,
            "page_size": page_size,
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# POST /api/perfil/logout/ — Logout con blacklist del refresh
# ============================================================


@extend_schema(
    summary="Logout con blacklist",
    description=(
        "Invalida (blacklistea) el refresh token recibido en el body. "
        "Después de llamar a este endpoint, ese refresh token no podrá "
        "volver a usarse para obtener nuevos access tokens."
    ),
    tags=["Auth"],
    request={
        "application/json": {
            "type": "object",
            "properties": {"refresh": {"type": "string"}},
            "required": ["refresh"],
            "example": {"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."},
        }
    },
    responses={
        205: {"description": "Sesión cerrada. Refresh token invalidado."},
        400: {"description": "Falta 'refresh' en el body."},
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def logout_view(request):
    refresh = request.data.get("refresh")
    if not refresh:
        return Response(
            {"detail": "refresh token requerido"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh)
        token.blacklist()  # ← aquí metemos el refresh en la lista negra
    except TokenError:
        # Si ya estaba invalidado o es inválido, no explotamos; devolvemos 205 igualmente
        pass

    # 205 Reset Content: indica que el cliente debe resetear el estado (borrar storage/cookies)
    return Response(status=status.HTTP_205_RESET_CONTENT)

# ============================================================
# POST /usuarios/<pk>/change-password/
# ============================================================
@extend_schema(
    summary="Cambiar la contraseña del usuario",
    description="Permite al usuario autenticado cambiar su contraseña proporcionando la antigua y la nueva.",
    tags=["Usuarios"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "old_password": {"type": "string"},
                "new_password": {"type": "string"},
            },
            "required": ["old_password", "new_password"],
        }
    },
    responses={
        200: OpenApiResponse(description="Contraseña cambiada correctamente."),
        400: OpenApiResponse(description="Contraseña actual incorrecta o datos inválidos."),
        401: OpenApiResponse(description="No autenticado.")
    }
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Seguridad: solo puede cambiar su propia contraseña (o moderador)
    is_moderator = getattr(getattr(request.user, "perfil", None), "moderator", False)
    if not is_moderator and request.user.id != user.id:
        raise PermissionDenied("No tienes permisos para cambiar esta contraseña.")

    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not user.check_password(old_password):
        return Response(
            {"detail": "La contraseña actual es incorrecta."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()

    return Response({"detail": "Contraseña cambiada correctamente."}, status=status.HTTP_200_OK)