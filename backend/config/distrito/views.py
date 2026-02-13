from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from distrito.models import Distrito
from distrito.serializers import DistritoSerializer


# GET /distritos/ — Listado de distritos ordenado por id descendente
@api_view(['GET'])
def distrito_list(request):
    qs = Distrito.objects.all().order_by('-id')
    serializer = DistritoSerializer(qs, many=True)
    return Response(serializer.data)


# GET /distritos/<int:pk>/ — Detalle de un distrito concreto
@api_view(['GET'])
def distrito_detail(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)  # NOTA: devuelve 404 si no existe
    serializer = DistritoSerializer(distrito)
    return Response(serializer.data)


# POST /distritos/create/ — Crear un nuevo distrito
@api_view(['POST'])
def distrito_create(request):
    serializer = DistritoSerializer(data=request.data)  # NOTA: incluye validaciones de nombre y código
    if serializer.is_valid():
        distrito = serializer.save()  # NOTA: crea el distrito con valores únicos
        return Response(DistritoSerializer(distrito).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /distritos/<int:pk>/update/ — Actualización completa del distrito
@api_view(['PUT'])
def distrito_update(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    serializer = DistritoSerializer(distrito, data=request.data)  # NOTA: actualización total (PUT)
    if serializer.is_valid():
        distrito = serializer.save()
        return Response(DistritoSerializer(distrito).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /distritos/<int:pk>/delete/ — Elimina un distrito
@api_view(['DELETE'])
def distrito_delete(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    distrito.delete()  # NOTA: elimina definitivamente el distrito
    return Response(status=status.HTTP_204_NO_CONTENT)