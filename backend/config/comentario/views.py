from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from core.permissions import IsAuthorOrModerator, IsModerator
from comentario.models import Comentario
from comentario.serializers import ComentarioSerializer


# GET /comentario/ — Listado de comentarios ordenados por fecha
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([])  # Cualquiera puede acceder
def comentario_list(request):
    qs = Comentario.objects.all().order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True)
    return Response(serializer.data)


# GET /comentario/<int:pk>/ — Detalle de un comentario por id
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([])  # Cualquiera puede acceder
def comentario_detail(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)  # NOTA: devuelve 404 si no existe
    serializer = ComentarioSerializer(comentario)
    return Response(serializer.data)


# GET /comentario/queja/<int:queja_id>/ — Comentarios asociados a una queja
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([])  # Cualquiera puede acceder
def comentarios_por_queja(request, queja_id):
    qs = Comentario.objects.filter(queja_id=queja_id).order_by('fecha_creacion')  # NOTA: mantiene orden cronológico
    serializer = ComentarioSerializer(qs, many=True)
    return Response(serializer.data)


# GET /comentario/user/<int:user_id>/ — Comentarios realizados por un usuario concreto
@api_view(['GET'])
@authentication_classes([])  # Sin autenticación
@permission_classes([])  # Cualquiera puede acceder
def comentarios_por_usuario(request, user_id):
    get_object_or_404(User, pk=user_id)  # NOTA: valida la existencia del usuario antes de filtrar
    qs = Comentario.objects.filter(autor_id=user_id).order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True)
    return Response(serializer.data)


# POST /comentario/create/ — Crea un nuevo comentario
@api_view(['POST'])
@authentication_classes([JWTAuthentication])  # Autenticación JWT
@permission_classes([IsAuthenticated])  # Solo usuarios autenticados pueden crear comentarios
def comentario_create(request):
    serializer = ComentarioSerializer(data=request.data)  # NOTA: incluye validaciones de contenido y coherencia del parent
    if serializer.is_valid():
        comentario = serializer.save()  # NOTA: persiste el comentario en la base de datos
        return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /comentario/<int:pk>/update/ — Actualización completa de un comentario
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])  # Autenticación JWT
@permission_classes([IsAuthenticated, IsAuthorOrModerator])  # Solo usuarios autenticados pueden actualizar comentarios
def comentario_update(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)  # NOTA: asegura existencia antes de actualizar
    serializer = ComentarioSerializer(comentario, data=request.data)  # NOTA: actualización total (PUT)
    if serializer.is_valid():
        comentario = serializer.save()
        return Response(ComentarioSerializer(comentario).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /comentario/<int:pk>/delete/ — Elimina un comentario
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])  # Autenticación JWT
@permission_classes([IsAuthenticated, IsAuthorOrModerator])  # Solo usuarios autenticados pueden
def comentario_delete(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)  # NOTA: devuelve 404 si no existe
    comentario.delete()  # NOTA: elimina el comentario de la base de datos
    return Response(status=status.HTTP_204_NO_CONTENT)