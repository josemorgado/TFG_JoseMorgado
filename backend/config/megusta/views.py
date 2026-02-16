from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample
)

from core.permissions import IsAuthorOrModerator
from .models import MeGusta
from .serializers import MeGustaSerializer


# ============================================================
# GET /megusta/ — Listado general
# ============================================================
@extend_schema(
    summary="Listar MeGusta",
    description="Devuelve el listado completo de likes ordenados por ID.",
    tags=["MeGusta"],
    responses={
        200: OpenApiResponse(response=MeGustaSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def megusta_list(request):
    qs = MeGusta.objects.all().order_by('id')
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /megusta/{pk}/ — Detalle
# ============================================================
@extend_schema(
    summary="Obtener detalle de un MeGusta",
    description="Retorna la información de un 'me gusta' concreto según su ID.",
    tags=["MeGusta"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del MeGusta a consultar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(response=MeGustaSerializer),
        404: OpenApiResponse(description="No encontrado"),
    }
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def megusta_detail(request, pk):
    mg = get_object_or_404(MeGusta, pk=pk)
    serializer = MeGustaSerializer(mg)
    return Response(serializer.data)


# ============================================================
# GET /megusta/queja/{queja_id}/ — Likes por queja
# ============================================================
@extend_schema(
    summary="Listar MeGusta asociados a una queja",
    description="Devuelve los likes otorgados a una queja concreta.",
    tags=["MeGusta"],
    parameters=[
        OpenApiParameter(
            name="queja_id",
            type=int,
            description="ID de la queja",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={200: OpenApiResponse(response=MeGustaSerializer(many=True))}
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def megusta_por_queja(request, queja_id):
    ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = MeGusta.objects.filter(content_type=ct, object_id=queja_id)
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# GET /megusta/comentario/{comentario_id}/ — Likes por comentario
# ============================================================
@extend_schema(
    summary="Listar MeGusta de un comentario",
    description="Devuelve los likes otorgados a un comentario concreto.",
    tags=["MeGusta"],
    parameters=[
        OpenApiParameter(
            name="comentario_id",
            type=int,
            description="ID del comentario",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={200: OpenApiResponse(response=MeGustaSerializer(many=True))}
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def megusta_por_comentario(request, comentario_id):
    ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = MeGusta.objects.filter(content_type=ct, object_id=comentario_id)
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# ============================================================
# POST /megusta/toggle/ — Alternar MeGusta
# ============================================================
@extend_schema(
    summary="Alternar MeGusta",
    description="Activa o desactiva un like sobre una queja o comentario, según el usuario autenticado.",
    tags=["MeGusta"],
    request=MeGustaSerializer,
    responses={
        200: OpenApiResponse(
            description="Devuelve si el like fue activado o eliminado",
            examples=[
                OpenApiExample(
                    "MeGusta activado",
                    value={"liked": True, "megusta": {"id": 12, "content_type": 7, "object_id": 4, "usuario": 2}},
                    response_only=True
                ),
                OpenApiExample(
                    "MeGusta eliminado",
                    value={"liked": False, "megusta": None},
                    response_only=True
                )
            ]
        ),
        400: OpenApiResponse(description="Datos inválidos"),
        401: OpenApiResponse(description="No autenticado"),
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def megusta_toggle(request):
    user = request.user
    serializer = MeGustaSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    content_type = serializer.validated_data['content_type']
    object_id = serializer.validated_data['object_id']

    model_cls = content_type.model_class()
    obj = get_object_or_404(model_cls, pk=object_id)

    liked, instance = MeGusta.objects.toggle_like(obj, user)

    return Response({
        'liked': liked,
        'megusta': MeGustaSerializer(instance).data if instance else None
    })


# ============================================================
# DELETE /megusta/{pk}/delete/ — Eliminar MeGusta
# ============================================================
@extend_schema(
    summary="Eliminar MeGusta",
    description="Elimina un like según su ID. Requiere ser autor o moderador.",
    tags=["MeGusta"],
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            description="ID del MeGusta a eliminar",
            required=True,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        204: OpenApiResponse(description="MeGusta eliminado"),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Permisos insuficientes"),
        404: OpenApiResponse(description="MeGusta no encontrado"),
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAuthorOrModerator])
def megusta_delete(request, pk):
    mg = get_object_or_404(MeGusta, pk=pk)
    mg.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)