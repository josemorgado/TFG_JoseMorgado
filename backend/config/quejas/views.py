from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.serializers import QuejaSerializer
from quejas.models import Queja

# Create your views here.

@api_view(['GET'])
def quejas_list(request):
    qs = Queja.objects.all().order_by('-id')[:10]
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def queja_detail(request, pk):
    try:
        queja = Queja.objects.get(pk=pk)
    except Queja.DoesNotExist:
        return Response({"detail": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = QuejaSerializer(queja)
    return Response(serializer.data)

@api_view(['POST'])
def queja_create(request):
    serializer = QuejaSerializer(data=request.data)
    if serializer.is_valid():
        queja = serializer.save()
        return Response(QuejaSerializer(queja).data, status=201)
    return Response(serializer.errors, status=400)

