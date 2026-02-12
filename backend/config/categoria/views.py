from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from categoria.models import Categoria
from categoria.serializers import CategoriaSerializer


# GET /categorias/ — Listado de categorías (ordenadas por id descendente)
@api_view(['GET'])
def categoria_list(request):
    qs = Categoria.objects.all().order_by('id')
    serializer = CategoriaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /categorias/<int:pk>/ — Detalle de una categoría por id
@api_view(['GET'])
def categoria_detail(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)  # NOTA: devuelve 404 si no existe
    serializer = CategoriaSerializer(categoria)
    return Response(serializer.data)


# POST /categorias/create/ — Crea una nueva categoría
@api_view(['POST'])
def categoria_create(request):
    serializer = CategoriaSerializer(data=request.data)  # NOTA: valida nombre y descripción
    if serializer.is_valid():
        categoria = serializer.save()  # NOTA: persiste y devuelve instancia creada
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /categorias/<int:pk>/update/ — Actualiza por completo una categoría existente
@api_view(['PUT'])
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)  # NOTA: asegura existencia antes de actualizar
    serializer = CategoriaSerializer(categoria, data=request.data)  # NOTA: actualización total (PUT)
    if serializer.is_valid():
        categoria = serializer.save()
        return Response(CategoriaSerializer(categoria).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /categorias/<int:pk>/delete/ — Elimina una categoría
@api_view(['DELETE'])
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)  # NOTA: 404 si no existe
    categoria.delete()  # NOTA: elimina la instancia de la base de datos
    return Response(status=status.HTTP_204_NO_CONTENT)


# POST /categorias/<int:pk>/toggle-estado/ — Alterna el campo 'activo' de la categoría
@api_view(['POST'])
def categoria_toggle_estado(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)  # NOTA: carga la categoría objetivo
    categoria.activo = not categoria.activo  # NOTA: invierte el estado actual
    categoria.save()  # NOTA: persiste el nuevo estado
    return Response(CategoriaSerializer(categoria).data, status=status.HTTP_200_OK)
