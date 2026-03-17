# stats/serializers.py
from rest_framework import serializers


class StatItemSerializer(serializers.Serializer):
    """
    Item genérico para rankings (categorías / distritos).
    - id: identificador de la categoría/distrito
    - nombre: nombre legible
    - total: número de quejas
    """
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    total = serializers.IntegerField()


class OverviewSerializer(serializers.Serializer):
    """
    KPIs globales para tarjetas resumen.
    - total: total de quejas
    - pen: pendientes (PEN)
    - enp: en progreso (ENP)
    - res: resueltas (RES)
    - rec: rechazadas (REC)
    """
    total = serializers.IntegerField()
    pen = serializers.IntegerField()
    enp = serializers.IntegerField()
    res = serializers.IntegerField()
    rec = serializers.IntegerField()


class EstadosSerializer(serializers.Serializer):
    """
    Distribución por estado.
    - PEN, ENP, RES, REC: recuentos por estado
    - total: suma de todos los estados
    """
    PEN = serializers.IntegerField()
    ENP = serializers.IntegerField()
    RES = serializers.IntegerField()
    REC = serializers.IntegerField()
    total = serializers.IntegerField()


class ByEstadoSerializer(serializers.Serializer):
    """
    Desglose por estado para un punto temporal.
    Los campos son opcionales para simplificar el formateo del response.
    """
    PEN = serializers.IntegerField(required=False, default=0)
    ENP = serializers.IntegerField(required=False, default=0)
    RES = serializers.IntegerField(required=False, default=0)
    REC = serializers.IntegerField(required=False, default=0)


class TimeSeriesPointSerializer(serializers.Serializer):
    """
    Punto de la serie temporal.
    - period: etiqueta del periodo (YYYY-MM, YYYY-Www, YYYY-MM-DD o YYYY)
    - total: total de quejas en ese periodo
    - by_estado: (opcional) desglose por estado cuando stack_by=estado
    """
    period = serializers.CharField()
    total = serializers.IntegerField()
    by_estado = ByEstadoSerializer(required=False)
