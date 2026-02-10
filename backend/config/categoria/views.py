from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from categoria.models import Categoria
from categoria.serializers import CategoriaSerializer


# GET /categorias/  → Listado de categorías
@api_view(['GET'])
def categoria_list(request):
    qs = Categoria.objects.all().order_by('-id')
    serializer = CategoriaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /categorias/<pk>/ → Detalle de una categoría
@api_view(['GET'])
def categoria_detail(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    serializer = CategoriaSerializer(categoria)
    return Response(serializer.data)


# POST /categorias/create/ → Crear categoría
@api_view(['POST'])
def categoria_create(request):
    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        categoria = serializer.save()
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /categorias/<pk>/update/ → Actualizar toda la categoría
@api_view(['PUT'])
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    serializer = CategoriaSerializer(categoria, data=request.data)
    if serializer.is_valid():
        categoria = serializer.save()
        return Response(CategoriaSerializer(categoria).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /categorias/<pk>/delete/ → Eliminar categoría
@api_view(['DELETE'])
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# POST /categorias/<pk>/toggle-estado/ → Alternar activo <-> inactivo
@api_view(['POST'])
def categoria_toggle_estado(request, pk):
    """
    POST  /categoria/<pk>/toggle-estado/  → alterna activo <-> inactivo
    """
    categoria = get_object_or_404(Categoria, pk=pk)

    categoria.activo = not categoria.activo

    categoria.save()
    return Response(CategoriaSerializer(categoria).data, status=status.HTTP_200_OK)
