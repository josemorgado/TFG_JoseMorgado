from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from quejas.serializers import QuejaSerializer
from quejas.models import Queja


# -----------------------------------------
# GET /quejas/  → Lista las todas las quejas
# -----------------------------------------
@api_view(['GET'])
def quejas_list(request):
    qs = Queja.objects.all().order_by('-id')
    serializer = QuejaSerializer(qs, many=True)  # salida: no hace falta context
    return Response(serializer.data)


# ------------------------------------------------------
# GET /quejas/<pk>/  → Devuelve el detalle de una queja
# ------------------------------------------------------
@api_view(['GET'])
def queja_detail(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    serializer = QuejaSerializer(queja)  # salida: no hace falta context
    return Response(serializer.data)


# ------------------------------------------------------------
# POST /quejas/  → Crea una queja nueva (valida con serializer)
# ------------------------------------------------------------
@api_view(['POST'])
def queja_create(request):
    # Tu serializer usa request en create/validate → pasar context
    serializer = QuejaSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        queja = serializer.save()
        return Response(QuejaSerializer(queja).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------
# PUT /quejas/<pk>/  → Reemplaza completamente una queja (update completo)
# ------------------------------------------------------------------------
@api_view(['PUT'])
def queja_update(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    # PUT = actualización total → partial=False
    serializer = QuejaSerializer(queja, data=request.data, context={'request': request})
    if serializer.is_valid():
        queja = serializer.save()
        return Response(QuejaSerializer(queja).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------------
# PATCH /quejas/<pk>/  → Actualiza parcialmente una queja (campos sueltos)
# -------------------------------------------------------------------------
@api_view(['PATCH'])
def queja_partial_update(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    # PATCH = actualización parcial → partial=True
    serializer = QuejaSerializer(queja, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        queja = serializer.save()
        return Response(QuejaSerializer(queja).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------------------------------------
# DELETE /quejas/<pk>/  → Elimina una queja por su identificador
# --------------------------------------------------------
@api_view(['DELETE'])
def queja_delete(request, pk):
    queja = get_object_or_404(Queja, pk=pk)
    queja.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------------------
# GET /quejas/categoria/<categoria_id>/  → Lista quejas filtradas por categoría concreta
# ---------------------------------------------------------------------------------------
@api_view(['GET'])
def quejas_por_categoria(request, categoria_id):
    qs = Queja.objects.filter(categoria_id=categoria_id).order_by('-id')
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)


# -----------------------------------------------------------------------------------
# GET /quejas/distrito/<distrito_id>/  → Lista quejas filtradas por distrito concreto
# -----------------------------------------------------------------------------------
@api_view(['GET'])
def quejas_por_distrito(request, distrito_id):
    qs = Queja.objects.filter(distrito_id=distrito_id).order_by('-id')
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)


# -----------------------------------------------------------------------------
# GET /quejas/autor/<autor_id>/  → Lista quejas creadas por un usuario (autor)
# -----------------------------------------------------------------------------
@api_view(['GET'])
def quejas_por_autor(request, autor_id):
    qs = Queja.objects.filter(autor_id=autor_id).order_by('-id')
    serializer = QuejaSerializer(qs, many=True)
    return Response(serializer.data)


# ---------------------------------------------------------------------------------------------------
# PATCH /quejas/<pk>/estado/  → Cambia SOLO el estado de la queja (sin tocar otros campos)
# ---------------------------------------------------------------------------------------------------
@api_view(['PATCH'])
def queja_cambiar_estado(request, pk):
    """
    Espera un body JSON con {"estado": "PEN" | "ENP" | "RES" | "REC"}
    """
    queja = get_object_or_404(Queja, pk=pk)

    # Solo permitimos cambiar el 'estado'
    estado = request.data.get('estado')
    if estado is None:
        return Response({"estado": ["Este campo es requerido."]}, status=status.HTTP_400_BAD_REQUEST)

    # Validación básica contra choices del modelo:
    valid_values = {choice[0] for choice in queja._meta.get_field('estado').choices}
    if estado not in valid_values:
        return Response({"estado": [f"Valor inválido. Debe ser uno de {sorted(valid_values)}"]},
                        status=status.HTTP_400_BAD_REQUEST)

    queja.estado = estado
    queja.save(update_fields=['estado', 'fecha_actualizacion'])
    return Response(QuejaSerializer(queja).data, status=status.HTTP_200_OK)