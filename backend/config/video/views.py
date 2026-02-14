from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Video
from .serializers import VideoSerializer


# GET /videos/ — Listado de videos ordenado por id descendente
@api_view(['GET'])
def video_list(request):
    qs = Video.objects.all().order_by('id')
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data)


# GET /videos/<int:pk>/ — Detalle de un video concreto
@api_view(['GET'])
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    serializer = VideoSerializer(video)
    return Response(serializer.data)


# GET /videos/queja/<int:queja_id>/ — Listado de videos por queja (orden por 'orden' asc.)
@api_view(['GET'])
def videos_por_queja(request, queja_id):
    # Ajusta 'app_label' y 'model' si tus nombres reales difieren
    queja_ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = Video.objects.filter(content_type=queja_ct, object_id=queja_id).order_by('orden')
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data)


# GET /videos/comentario/<int:comentario_id>/ — Listado de videos por comentario (orden por 'orden' asc.)
@api_view(['GET'])
def videos_por_comentario(request, comentario_id):
    # Cambia aquí si tu app real se llama distinto (p. ej., 'comentarios')
    comentario_ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = Video.objects.filter(content_type=comentario_ct, object_id=comentario_id).order_by('orden')
    serializer = VideoSerializer(qs, many=True)
    return Response(serializer.data)


# POST /videos/create/ — Sube un video y asigna 'orden' automáticamente por objeto
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def video_create(request):
    # Valida payload multipart/form y existencia del objeto asociado
    serializer = VideoSerializer(data=request.data)

    if serializer.is_valid():
        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']

        # Obtener videos existentes del mismo objeto para calcular el siguiente 'orden'
        qs = Video.objects.filter(content_type=content_type, object_id=object_id)

        # Calcular el siguiente 'orden' (0 si no hay anteriores)
        if qs.exists():
            ultimo = qs.order_by('-orden').first()
            nuevo_orden = ultimo.orden + 1
        else:
            nuevo_orden = 0

        try:
            # Guardar video con el 'orden' asignado
            video = serializer.save(orden=nuevo_orden)
        except DjangoValidationError as e:
            # Captura de ValidationError del modelo (por ejemplo, MAX_VIDEOS)
            payload = {'detail': e.message_dict if hasattr(e, 'message_dict') else e.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE /videos/<int:pk>/delete/ — Elimina un video
@api_view(['DELETE'])
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    video.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)