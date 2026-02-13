# usuarios/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserLiteSerializer, UserPerfilSerializer
from .models import Perfil

User = get_user_model()


# GET /usuarios/ → Lista de usuarios con perfil embebido
@api_view(['GET'])
def usuario_list(request):
    # Cargamos el perfil junto con el usuario para evitar N+1
    qs = User.objects.select_related('perfil').all().order_by('-id')
    serializer = UserPerfilSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# GET /usuarios/<int:pk>/ → Detalle de usuario + perfil
@api_view(['GET'])
def usuario_detail(request, pk):
    user = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
    serializer = UserPerfilSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# POST /usuarios/create/ → Crea User + Perfil (acepta multipart para foto_perfil)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([AllowAny])  # cámbialo a IsAuthenticated si lo necesitas
def usuario_create(request):
    serializer = UserPerfilSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Recargar la instancia con el perfil ya persistido
    user = User.objects.select_related('perfil').get(pk=user.pk)

    # Devolver con el mismo serializer y contexto
    return Response(
        UserPerfilSerializer(user, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


# PUT /usuarios/<int:pk>/update/ → Actualización completa de User + Perfil
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_update(request, pk):
    user = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
    serializer = UserPerfilSerializer(user, data=request.data, context={'request': request})  # PUT → partial=False
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Recargar para asegurar que el perfil actualizado está en la instancia
    user = User.objects.select_related('perfil').get(pk=user.pk)

    return Response(UserPerfilSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)


# PATCH /usuarios/<int:pk>/partial-update/ → Actualización parcial de User + Perfil
@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def usuario_partial_update(request, pk):
    user = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
    serializer = UserPerfilSerializer(user, data=request.data, partial=True, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Recargar para asegurar consistencia en la respuesta
    user = User.objects.select_related('perfil').get(pk=user.pk)

    return Response(UserPerfilSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)


# DELETE /usuarios/<int:pk>/delete/ → Elimina User (Perfil cae por CASCADE)
@api_view(['DELETE'])
def usuario_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)