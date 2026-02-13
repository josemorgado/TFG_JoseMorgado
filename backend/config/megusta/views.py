from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from .models import MeGusta
from .serializers import MeGustaSerializer


# GET /megusta/ — Listado de 'me gusta' ordenado por id descendente
@api_view(['GET'])
def megusta_list(request):
    qs = MeGusta.objects.all().order_by('-id')
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /megusta/<int:pk>/ — Detalle de un 'me gusta' concreto
@api_view(['GET'])
def megusta_detail(request, pk):
    mg = get_object_or_404(MeGusta, pk=pk)  # devuelve 404 si no existe
    serializer = MeGustaSerializer(mg)
    return Response(serializer.data)


# GET /megusta/queja/<int:queja_id>/ — Listado por queja
@api_view(['GET'])
def megusta_por_queja(request, queja_id):
    ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = MeGusta.objects.filter(content_type=ct, object_id=queja_id)
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /megusta/comentario/<int:comentario_id>/ — Listado por comentario
@api_view(['GET'])
def megusta_por_comentario(request, comentario_id):
    ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = MeGusta.objects.filter(content_type=ct, object_id=comentario_id)
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# POST /megusta/toggle/ — Alterna like para usuario autenticado sobre una queja o comentario
# NOTA: necesita testing tras implementar autenticación de usuarios
@api_view(['POST'])
def megusta_toggle(request):
    user = request.user
    if not user or not user.is_authenticated:
        return Response({'detail': 'No autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = MeGustaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    content_type = serializer.validated_data['content_type']
    object_id = serializer.validated_data['object_id']

    # Se obtiene la instancia real del modelo asociado
    model_cls = content_type.model_class()
    obj = get_object_or_404(model_cls, pk=object_id)

    # Alterna el 'me gusta' usando el manager del modelo
    liked, instance = MeGusta.objects.toggle_like(obj, user)

    return Response({
        'liked': liked,  # True = ahora tiene like, False = se quitó
        'megusta': MeGustaSerializer(instance).data if instance else None
    })


# DELETE /megusta/<int:pk>/delete/ — Elimina un 'me gusta'
@api_view(['DELETE'])
def megusta_delete(request, pk):
    mg = get_object_or_404(MeGusta, pk=pk)
    mg.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)