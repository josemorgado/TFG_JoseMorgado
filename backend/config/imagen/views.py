from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from .models import Imagen
from .serializers import ImagenSerializer


# GET /imagenes/
@api_view(['GET'])
def imagen_list(request):
    qs = Imagen.objects.all().order_by('-id')
    serializer = ImagenSerializer(qs, many=True)
    return Response(serializer.data)


# GET /imagenes/<pk>/
@api_view(['GET'])
def imagen_detail(request, pk):
    imagen = get_object_or_404(Imagen, pk=pk)
    serializer = ImagenSerializer(imagen)
    return Response(serializer.data)

# GET /imagenes/queja/<queja_id>/
@api_view(['GET'])
def imagenes_por_queja(request, queja_id):
    queja_ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = Imagen.objects.filter(content_type=queja_ct, object_id=queja_id).order_by('orden')
    serializer = ImagenSerializer(qs, many=True)
    return Response(serializer.data)


# GET /imagenes/comentario/<comentario_id>/
@api_view(['GET'])
def imagenes_por_comentario(request, comentario_id):
    comentario_ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = Imagen.objects.filter(content_type=comentario_ct, object_id=comentario_id).order_by('orden')
    serializer = ImagenSerializer(qs, many=True)
    return Response(serializer.data)



# POST /imagenes/create/

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def imagen_create(request):
    serializer = ImagenSerializer(data=request.data)

    if serializer.is_valid():
        print(serializer.validated_data)
        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']

        # Obtener las imágenes ya existentes del mismo objeto
        qs = Imagen.objects.filter(
            content_type=content_type,
            object_id=object_id
        )

        # Calcular el orden correcto
        if qs.exists():
            ultimo = qs.order_by('-orden').first()
            nuevo_orden = ultimo.orden + 1
        else:
            nuevo_orden = 0

        # Guardar imagen aplicando el orden automático
        imagen = serializer.save(orden=nuevo_orden)

        return Response(
            ImagenSerializer(imagen).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE /imagenes/<pk>/delete/
@api_view(['DELETE'])
def imagen_delete(request, pk):
    imagen = get_object_or_404(Imagen, pk=pk)
    imagen.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


