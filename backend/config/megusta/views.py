# megusta/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated

from .models import MeGusta
from .serializers import MeGustaSerializer


# GET /megusta/
@api_view(['GET'])
def megusta_list(request):
    qs = MeGusta.objects.all().order_by('-id')
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /megusta/<pk>/
@api_view(['GET'])
def megusta_detail(request, pk):
    mg = get_object_or_404(MeGusta, pk=pk)
    serializer = MeGustaSerializer(mg)
    return Response(serializer.data)


# GET /megusta/queja/<queja_id>/
@api_view(['GET'])
def megusta_por_queja(request, queja_id):
    ct = ContentType.objects.get(app_label='quejas', model='queja')
    qs = MeGusta.objects.filter(content_type=ct, object_id=queja_id)
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# GET /megusta/comentario/<comentario_id>/
@api_view(['GET'])
def megusta_por_comentario(request, comentario_id):
    ct = ContentType.objects.get(app_label='comentario', model='comentario')
    qs = MeGusta.objects.filter(content_type=ct, object_id=comentario_id)
    serializer = MeGustaSerializer(qs, many=True)
    return Response(serializer.data)


# POST /megusta/toggle/
# Este endpoint permite a un usuario autenticado dar o quitar "me gusta" a una queja o comentario.
# Necesita testing tras implementar autenticacion de usuarios
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

    # Creamos una instancia "falsa" solo para pasarla al manager
    model_cls = content_type.model_class()
    obj = get_object_or_404(model_cls, pk=object_id)

    liked, instance = MeGusta.objects.toggle_like(obj, user)

    return Response({
        'liked': liked,  # True = ahora tiene like, False = se quitó
        'megusta': MeGustaSerializer(instance).data if instance else None
    })
    

# DELETE /megusta/<pk>/delete/
@api_view(['DELETE'])
def megusta_delete(request, pk):
    mg = get_object_or_404(MeGusta, pk=pk)
    mg.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)