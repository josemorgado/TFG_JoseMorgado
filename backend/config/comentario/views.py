from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from comentario.models import Comentario
from comentario.serializers import ComentarioSerializer


# GET /comentario/  → Listado de comentarios
@api_view(['GET'])
def comentario_list(request):
    qs = Comentario.objects.all().order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True)
    return Response(serializer.data)


# GET /comentario/<pk>/ → Detalle de comentario
@api_view(['GET'])
def comentario_detail(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    serializer = ComentarioSerializer(comentario)
    return Response(serializer.data)


# GET /comentario/queja/<queja_id>/ → Comentarios por queja
@api_view(['GET'])
def comentarios_por_queja(request, queja_id):
    qs = Comentario.objects.filter(queja_id=queja_id).order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True)
    return Response(serializer.data)


# GET /comentario/user/<user_id>/ → Comentarios por usuario
@api_view(['GET'])
def comentarios_por_usuario(request, user_id):
    # Si quieres validar que el usuario exista:
    get_object_or_404(User, pk=user_id)
    qs = Comentario.objects.filter(autor_id=user_id).order_by('fecha_creacion')
    serializer = ComentarioSerializer(qs, many=True)
    return Response(serializer.data)


# POST /comentario/create/ → Crear comentario
@api_view(['POST'])
def comentario_create(request):
    serializer = ComentarioSerializer(data=request.data)
    if serializer.is_valid():
        comentario = serializer.save()
        return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /comentario/<pk>/update/ → Actualizar comentario completo
@api_view(['PUT'])
def comentario_update(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    serializer = ComentarioSerializer(comentario, data=request.data)
    if serializer.is_valid():
        comentario = serializer.save()
        return Response(ComentarioSerializer(comentario).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE /comentario/<pk>/delete/ → Borrar comentario
@api_view(['DELETE'])
def comentario_delete(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)