from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from distrito.models import Distrito
from distrito.serializers import DistritoSerializer


# GET /distrito/ → Listado de distritos
@api_view(['GET'])
def distrito_list(request):
    qs = Distrito.objects.all().order_by('-id')
    serializer = DistritoSerializer(qs, many=True)
    return Response(serializer.data)


# GET /distrito/<pk>/ → Detalle de un distrito
@api_view(['GET'])
def distrito_detail(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    serializer = DistritoSerializer(distrito)
    return Response(serializer.data)


# POST /distrito/create/ → Crear distrito
@api_view(['POST'])
def distrito_create(request):
    serializer = DistritoSerializer(data=request.data)
    if serializer.is_valid():
        distrito = serializer.save()
        return Response(DistritoSerializer(distrito).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT /distrito/<pk>/update/ → Actualizar todo el distrito
@api_view(['PUT'])
def distrito_update(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    serializer = DistritoSerializer(distrito, data=request.data)
    if serializer.is_valid():
        distrito = serializer.save()
        return Response(DistritoSerializer(distrito).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /distrito/<pk>/delete/ → Eliminar distrito
@api_view(['DELETE'])
def distrito_delete(request, pk):
    distrito = get_object_or_404(Distrito, pk=pk)
    distrito.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)