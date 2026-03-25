# stats/views.py
from datetime import datetime
from typing import List, Optional

# --- Django ORM ---
from django.db.models import Count, Q, Min, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear

# --- DRF ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# --- Models ---
from quejas.models import Queja
from categoria.models import Categoria
from distrito.models import Distrito
from respuesta.models import Respuesta

# --- OpenAPI ---
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

# --- Serializers ---
from stats.serializers import (
    StatItemSerializer,
    OverviewSerializer,
    EstadosSerializer,
    TimeSeriesPointSerializer,
)


# ============================================================
# HELPERS
# ============================================================

def _parse_date(value):
    """Devuelve date o None si es inválida (espera YYYY-MM-DD)."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_bool(value, default=False) -> bool:
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "t", "yes", "y")


def _parse_estado_list(value: Optional[str]) -> Optional[List[str]]:
    """
    Convierte 'PEN,ENP,RES' -> ['PEN','ENP','RES'] validando contra choices.
    """
    if not value:
        return None
    raw = [v.strip().upper() for v in value.split(",") if v.strip()]
    valid = {"PEN", "ENP", "RES", "REC"}
    invalid = [v for v in raw if v not in valid]
    if invalid:
        raise ValueError(f"Estado(s) inválido(s): {invalid}.")
    return list(dict.fromkeys(raw))  # Elimina duplicados conservando orden


# ============================================================
#  QUEJAS - CATEGORÍAS
# ============================================================

@extend_schema(
    summary="Categorías más usadas",
    description=(
        "Devuelve un ranking de categorías según número de quejas que "
        "cumplen los filtros."
    ),
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=StatItemSerializer(many=True))}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_categorias(request):
    # --- lectura de parámetros
    user_id = request.query_params.get("user_id")
    limit = int(request.query_params.get("limit", 5))
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    distrito_id = request.query_params.get("distrito_id")
    include_zero = _parse_bool(request.query_params.get("include_zero"))
    ordering = request.query_params.get("ordering", "-total")

    if ordering not in ("-total", "total", "nombre"):
        return Response({"detail": "ordering inválido"}, status=400)

    # --- filtros
    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if estados:
        q &= Q(estado__in=estados)
    if distrito_id:
        q &= Q(distrito_id=distrito_id)

    # --- consulta
    qs = (
        Queja.objects.filter(q)
        .values("categoria_id", "categoria__nombre")
        .annotate(total=Count("id"))
    )

    # ordering
    if ordering == "nombre":
        qs = qs.order_by("categoria__nombre")
    elif ordering == "total":
        qs = qs.order_by("total")
    else:
        qs = qs.order_by("-total")

    if limit:
        qs = qs[:limit]

    data = [
        {"id": r["categoria_id"], "nombre": r["categoria__nombre"], "total": r["total"]}
        for r in qs
    ]

    return Response(data)


# ============================================================
#  QUEJAS - DISTRITOS
# ============================================================

@extend_schema(
    summary="Distritos con más quejas",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=StatItemSerializer(many=True))}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_distritos(request):
    user_id = request.query_params.get("user_id")
    limit = int(request.query_params.get("limit", 5))
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    include_zero = _parse_bool(request.query_params.get("include_zero"))
    ordering = request.query_params.get("ordering", "-total")

    if ordering not in ("-total", "total", "nombre"):
        return Response({"detail": "ordering inválido"}, status=400)

    q = Q()
    if user_id: q &= Q(autor_id=user_id)
    if desde: q &= Q(fecha_creacion__date__gte=desde)
    if hasta: q &= Q(fecha_creacion__date__lte=hasta)
    if estados: q &= Q(estado__in=estados)
    if categoria_id: q &= Q(categoria_id=categoria_id)

    qs = (
        Queja.objects.filter(q)
        .values("distrito_id", "distrito__nombre")
        .annotate(total=Count("id"))
    )

    if ordering == "nombre":
        qs = qs.order_by("distrito__nombre")
    elif ordering == "total":
        qs = qs.order_by("total")
    else:
        qs = qs.order_by("-total")

    if limit: qs = qs[:limit]

    return Response([
        {"id": r["distrito_id"], "nombre": r["distrito__nombre"], "total": r["total"]}
        for r in qs
    ])


# ============================================================
#  QUEJAS - OVERVIEW
# ============================================================

@extend_schema(
    summary="KPIs de quejas",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=OverviewSerializer)}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_overview(request):
    user_id = request.query_params.get("user_id")
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    distrito_id = request.query_params.get("distrito_id")

    q = Q()
    if user_id: q &= Q(autor_id=user_id)
    if desde: q &= Q(fecha_creacion__date__gte=desde)
    if hasta: q &= Q(fecha_creacion__date__lte=hasta)
    if categoria_id: q &= Q(categoria_id=categoria_id)
    if distrito_id: q &= Q(distrito_id=distrito_id)
    if estados: q &= Q(estado__in=estados)

    agg = Queja.objects.filter(q).aggregate(
        total=Count("id"),
        pen=Count("id", filter=Q(estado="PEN")),
        enp=Count("id", filter=Q(estado="ENP")),
        res=Count("id", filter=Q(estado="RES")),
        rec=Count("id", filter=Q(estado="REC")),
    )

    return Response({k: int(agg.get(k, 0) or 0) for k in agg})


# ============================================================
#  QUEJAS - ESTADOS
# ============================================================

@extend_schema(
    summary="Distribución por estado",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=EstadosSerializer)}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_estados(request):
    user_id = request.query_params.get("user_id")
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    distrito_id = request.query_params.get("distrito_id")

    q = Q()
    if user_id: q &= Q(autor_id=user_id)
    if desde: q &= Q(fecha_creacion__date__gte=desde)
    if hasta: q &= Q(fecha_creacion__date__lte=hasta)
    if categoria_id: q &= Q(categoria_id=categoria_id)
    if distrito_id: q &= Q(distrito_id=distrito_id)
    if estados: q &= Q(estado__in=estados)

    base = Queja.objects.filter(q)

    data = {
        "PEN": base.filter(estado="PEN").count(),
        "ENP": base.filter(estado="ENP").count(),
        "RES": base.filter(estado="RES").count(),
        "REC": base.filter(estado="REC").count(),
    }
    data["total"] = sum(data.values())
    return Response(data)


# ============================================================
#  QUEJAS - TIME SERIES
# ============================================================

@extend_schema(
    summary="Serie temporal de quejas",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=TimeSeriesPointSerializer(many=True))}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_timeseries(request):
    group_by = (request.query_params.get("group_by") or "month").lower()
    if group_by not in {"day", "week", "month", "year"}:
        return Response({"detail": "group_by inválido"}, status=400)

    stack_by = (request.query_params.get("stack_by") or "none").lower()
    if stack_by not in {"none", "estado"}:
        return Response({"detail": "stack_by inválido"}, status=400)

    user_id = request.query_params.get("user_id")
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    distrito_id = request.query_params.get("distrito_id")

    q = Q()
    if user_id: q &= Q(autor_id=user_id)
    if desde: q &= Q(fecha_creacion__date__gte=desde)
    if hasta: q &= Q(fecha_creacion__date__lte=hasta)
    if categoria_id: q &= Q(categoria_id=categoria_id)
    if distrito_id: q &= Q(distrito_id=distrito_id)
    if estados: q &= Q(estado__in=estados)

    trunc_map = {
        "day": TruncDay,
        "week": TruncWeek,
        "month": TruncMonth,
        "year": TruncYear,
    }
    trunc_fn = trunc_map[group_by]

    qs = (
        Queja.objects.filter(q)
        .annotate(period_dt=trunc_fn("fecha_creacion"))
        .values("period_dt")
    )

    if stack_by == "estado":
        qs = qs.annotate(
            total=Count("id"),
            PEN=Count("id", filter=Q(estado="PEN")),
            ENP=Count("id", filter=Q(estado="ENP")),
            RES=Count("id", filter=Q(estado="RES")),
            REC=Count("id", filter=Q(estado="REC")),
        )
    else:
        qs = qs.annotate(total=Count("id"))

    qs = qs.order_by("period_dt")

    data = []
    for row in qs:
        dt = row["period_dt"]
        if not dt:
            continue
        if group_by == "day":
            label = dt.strftime("%Y-%m-%d")
        elif group_by == "week":
            iso = dt.isocalendar()
            label = f"{iso.year}-W{iso.week:02d}"
        elif group_by == "month":
            label = dt.strftime("%Y-%m")
        else:
            label = dt.strftime("%Y")

        item = {"period": label, "total": int(row["total"])}
        if stack_by == "estado":
            item["by_estado"] = {
                "PEN": int(row.get("PEN", 0)),
                "ENP": int(row.get("ENP", 0)),
                "RES": int(row.get("RES", 0)),
                "REC": int(row.get("REC", 0)),
            }
        data.append(item)

    return Response(data)


# ============================================================
#  RESPUESTAS - KPIs
# ============================================================

@extend_schema(
    summary="KPIs de respuestas",
    description="Estadísticas agregadas de respuestas.",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(description="KPIs de respuestas")}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_respuestas_overview(request):

    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    q = Q()
    if desde: q &= Q(fecha_respuesta__date__gte=desde)
    if hasta: q &= Q(fecha_respuesta__date__lte=hasta)

    base = Respuesta.objects.filter(q)

    total_quejas_respondidas = base.values("queja_id").distinct().count()

    counts = base.values("queja_id").annotate(c=Count("id")).aggregate(avg=Avg("c"))
    media_respuestas = counts["avg"] or 0

    primeras = (
        base.values("queja_id")
        .annotate(first=Min("fecha_respuesta"))
        .annotate(
            delta=ExpressionWrapper(
                F("first") - F("queja__fecha_creacion"), output_field=DurationField()
            )
        )
    )

    tiempos = [p["delta"].total_seconds() for p in primeras if p["delta"]]
    tiempo_medio = sum(tiempos) / len(tiempos) if tiempos else 0

    return Response({
        "tiempo_medio_primera": tiempo_medio,
        "media_respuestas_por_queja": round(media_respuestas, 2),
        "total_quejas_respondidas": total_quejas_respondidas,
    })


# ============================================================
#  RESPUESTAS - TIME SERIES
# ============================================================

@extend_schema(
    summary="Serie temporal de respuestas",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=TimeSeriesPointSerializer(many=True))}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_respuestas_timeseries(request):

    group_by = (request.query_params.get("group_by") or "month").lower()
    if group_by not in {"day", "week", "month", "year"}:
        return Response({"detail": "group_by inválido"}, status=400)

    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    q = Q()
    if desde: q &= Q(fecha_respuesta__date__gte=desde)
    if hasta: q &= Q(fecha_respuesta__date__lte=hasta)

    trunc_map = {
        "day": TruncDay,
        "week": TruncWeek,
        "month": TruncMonth,
        "year": TruncYear,
    }

    trunc_fn = trunc_map[group_by]

    qs = (
        Respuesta.objects.filter(q)
        .annotate(period_dt=trunc_fn("fecha_respuesta"))
        .values("period_dt")
        .annotate(total=Count("id"))
        .order_by("period_dt")
    )

    data = []
    for row in qs:
        dt = row["period_dt"]
        if not dt:
            continue

        label = (
            dt.strftime("%Y-%m-%d") if group_by == "day" else
            f"{dt.year}-W{dt.isocalendar().week:02d}" if group_by == "week" else
            dt.strftime("%Y-%m") if group_by == "month" else
            dt.strftime("%Y")
        )

        data.append({"period": label, "total": int(row["total"])})

    return Response(data)


# ============================================================
#  RESPUESTAS - CATEGORÍAS
# ============================================================

@extend_schema(
    summary="Categorías con más respuestas",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=StatItemSerializer(many=True))}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_respuestas_categorias(request):

    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    q = Q()
    if desde: q &= Q(fecha_respuesta__date__gte=desde)
    if hasta: q &= Q(fecha_respuesta__date__lte=hasta)

    qs = (
        Respuesta.objects.filter(q)
        .values("queja__categoria_id", "queja__categoria__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return Response([
        {"id": r["queja__categoria_id"], "nombre": r["queja__categoria__nombre"], "total": r["total"]}
        for r in qs
    ])


# ============================================================
#  RESPUESTAS - DISTRITOS
# ============================================================

@extend_schema(
    summary="Distritos con más respuestas",
    tags=["Estadísticas"],
    responses={200: OpenApiResponse(response=StatItemSerializer(many=True))}
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_respuestas_distritos(request):

    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))

    q = Q()
    if desde: q &= Q(fecha_respuesta__date__gte=desde)
    if hasta: q &= Q(fecha_respuesta__date__lte=hasta)

    qs = (
        Respuesta.objects.filter(q)
        .values("queja__distrito_id", "queja__distrito__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return Response([
        {"id": r["queja__distrito_id"], "nombre": r["queja__distrito__nombre"], "total": r["total"]}
        for r in qs
    ])
