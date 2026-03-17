# stats/views.py
from datetime import datetime
from typing import List, Optional

from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from quejas.models import Queja
from categoria.models import Categoria
from distrito.models import Distrito

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from stats.serializers import (
    StatItemSerializer,
    OverviewSerializer,
    EstadosSerializer,
    TimeSeriesPointSerializer,
)


# ----------------------------
# Helpers parsing
# ----------------------------
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
    Devuelve None si no se ha pasado nada.
    Lanza ValueError si hay algún valor inválido.
    """
    if not value:
        return None
    raw = [v.strip().upper() for v in value.split(",") if v.strip()]
    valid = {"PEN", "ENP", "RES", "REC"}
    invalid = [v for v in raw if v not in valid]
    if invalid:
        raise ValueError(
            f"Valor(es) de 'estado' inválido(s): {invalid}. Use PEN, ENP, RES o REC (separados por coma)."
        )
    # eliminar duplicados conservando orden
    seen = set()
    dedup = []
    for v in raw:
        if v not in seen:
            dedup.append(v)
            seen.add(v)
    return dedup


# ============================================
# GET /stats/categorias/  → categorías más usadas
# ============================================
@extend_schema(
    summary="Categorías más usadas",
    description=(
        "Devuelve un ranking de categorías según número de quejas que cumplen los filtros.\n\n"
        "**Parámetros soportados (querystring):**\n"
        "- `user_id`: int (filtra por autor)\n"
        "- `limit`: int (por defecto 5)\n"
        "- `desde`: fecha `YYYY-MM-DD`\n"
        "- `hasta`: fecha `YYYY-MM-DD`\n"
        "- `estado`: permite múltiples en CSV `PEN,ENP,RES,REC`\n"
        "- `distrito_id`: int\n"
        "- `include_zero`: bool (incluir categorías sin ninguna queja)\n"
        "- `ordering`: `-total` (default) | `total` | `nombre`"
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(
            name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Número de resultados (default 5)",
        ),
        OpenApiParameter(
            name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="estado",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Permite múltiples (CSV): PEN,ENP,RES,REC",
        ),
        OpenApiParameter(
            name="distrito_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="include_zero", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="`-total` (default) | `total` | `nombre`",
        ),
    ],
    responses={
        200: OpenApiResponse(response=StatItemSerializer(many=True)),
        400: OpenApiResponse(description="Parámetro inválido"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo básico",
            value=[
                {"id": 3, "nombre": "Vía pública", "total": 42},
                {"id": 1, "nombre": "Limpieza", "total": 27},
            ],
            response_only=True,
        )
    ],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_categorias(request):
    # --- lectura de parámetros
    user_id = request.query_params.get("user_id")
    limit_raw = request.query_params.get("limit", "5")
    try:
        limit = int(limit_raw)
    except ValueError:
        return Response({"detail": "Parametro 'limit' inválido."}, status=400)

    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))
    if request.query_params.get("desde") and desde is None:
        return Response(
            {"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400
        )
    if request.query_params.get("hasta") and hasta is None:
        return Response(
            {"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400
        )

    # múltiple estados (CSV)
    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    distrito_id = request.query_params.get("distrito_id")
    include_zero = _parse_bool(request.query_params.get("include_zero"), default=False)
    ordering = request.query_params.get("ordering", "-total")
    if ordering not in ("-total", "total", "nombre"):
        return Response(
            {
                "detail": "Parametro 'ordering' inválido. Use '-total', 'total' o 'nombre'."
            },
            status=400,
        )

    # --- filtros para consultas basadas en Queja
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

    if include_zero:
        # Partimos de Categoria y anotamos count filtrado sobre relación 'quejas'
        q_rel = Q()
        if user_id:
            q_rel &= Q(quejas__autor_id=user_id)
        if desde:
            q_rel &= Q(quejas__fecha_creacion__date__gte=desde)
        if hasta:
            q_rel &= Q(quejas__fecha_creacion__date__lte=hasta)
        if estados:
            q_rel &= Q(quejas__estado__in=estados)
        if distrito_id:
            q_rel &= Q(quejas__distrito_id=distrito_id)

        qs = Categoria.objects.values("id", "nombre").annotate(
            total=Count("quejas", filter=q_rel)
        )
        if ordering == "nombre":
            qs = qs.order_by("nombre")
        elif ordering == "total":
            qs = qs.order_by("total")
        else:
            qs = qs.order_by("-total")
        if limit:
            qs = qs[:limit]

        data = [
            {"id": row["id"], "nombre": row["nombre"], "total": row["total"] or 0}
            for row in qs
        ]
    else:
        # Solo categorías con alguna queja que cumpla filtros
        qs = (
            Queja.objects.filter(q)
            .values("categoria_id", "categoria__nombre")
            .annotate(total=Count("id"))
        )
        if ordering == "nombre":
            qs = qs.order_by("categoria__nombre")
        elif ordering == "total":
            qs = qs.order_by("total")
        else:
            qs = qs.order_by("-total")
        if limit:
            qs = qs[:limit]

        data = [
            {
                "id": row["categoria_id"],
                "nombre": row["categoria__nombre"],
                "total": row["total"],
            }
            for row in qs
        ]

    return Response(data)


# ============================================
# GET /stats/distritos/ → distritos más usados
# ============================================
@extend_schema(
    summary="Distritos con más quejas",
    description=(
        "Devuelve un ranking de distritos según número de quejas que cumplen los filtros.\n\n"
        "**Parámetros soportados (querystring):**\n"
        "- `user_id`: int (filtra por autor)\n"
        "- `limit`: int (por defecto 5)\n"
        "- `desde`: fecha `YYYY-MM-DD`\n"
        "- `hasta`: fecha `YYYY-MM-DD`\n"
        "- `estado`: permite múltiples en CSV `PEN,ENP,RES,REC`\n"
        "- `categoria_id`: int\n"
        "- `include_zero`: bool (incluir distritos sin ninguna queja)\n"
        "- `ordering`: `-total` (default) | `total` | `nombre`"
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(
            name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Número de resultados (default 5)",
        ),
        OpenApiParameter(
            name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="estado",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Permite múltiples (CSV): PEN,ENP,RES,REC",
        ),
        OpenApiParameter(
            name="categoria_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="include_zero", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="`-total` (default) | `total` | `nombre`",
        ),
    ],
    responses={
        200: OpenApiResponse(response=StatItemSerializer(many=True)),
        400: OpenApiResponse(description="Parámetro inválido"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo básico",
            value=[
                {"id": 1, "nombre": "Centro", "total": 35},
                {"id": 2, "nombre": "Norte", "total": 18},
            ],
            response_only=True,
        )
    ],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_distritos(request):
    # --- lectura de parámetros
    user_id = request.query_params.get("user_id")
    limit_raw = request.query_params.get("limit", "5")
    try:
        limit = int(limit_raw)
    except ValueError:
        return Response({"detail": "Parametro 'limit' inválido."}, status=400)

    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))
    if request.query_params.get("desde") and desde is None:
        return Response(
            {"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400
        )
    if request.query_params.get("hasta") and hasta is None:
        return Response(
            {"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400
        )

    # múltiple estados (CSV)
    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    include_zero = _parse_bool(request.query_params.get("include_zero"), default=False)
    ordering = request.query_params.get("ordering", "-total")
    if ordering not in ("-total", "total", "nombre"):
        return Response(
            {
                "detail": "Parametro 'ordering' inválido. Use '-total', 'total' o 'nombre'."
            },
            status=400,
        )

    # --- filtros para consultas basadas en Queja
    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if estados:
        q &= Q(estado__in=estados)
    if categoria_id:
        q &= Q(categoria_id=categoria_id)

    if include_zero:
        # Partimos de Distrito y anotamos count de quejas relacionadas
        q_rel = Q()
        if user_id:
            q_rel &= Q(quejas__autor_id=user_id)
        if desde:
            q_rel &= Q(quejas__fecha_creacion__date__gte=desde)
        if hasta:
            q_rel &= Q(quejas__fecha_creacion__date__lte=hasta)
        if estados:
            q_rel &= Q(quejas__estado__in=estados)
        if categoria_id:
            q_rel &= Q(quejas__categoria_id=categoria_id)

        qs = Distrito.objects.values("id", "nombre").annotate(
            total=Count("quejas", filter=q_rel)
        )
        if ordering == "nombre":
            qs = qs.order_by("nombre")
        elif ordering == "total":
            qs = qs.order_by("total")
        else:
            qs = qs.order_by("-total")
        if limit:
            qs = qs[:limit]

        data = [
            {"id": row["id"], "nombre": row["nombre"], "total": row["total"] or 0}
            for row in qs
        ]
    else:
        # Solo distritos con alguna queja que cumpla filtros
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
        if limit:
            qs = qs[:limit]

        data = [
            {
                "id": row["distrito_id"],
                "nombre": row["distrito__nombre"],
                "total": row["total"],
            }
            for row in qs
        ]

    return Response(data)


# ============================================
# GET /stats/overview/ → KPIs (totales por estado)
# ============================================
@extend_schema(
    summary="KPIs de quejas",
    description=(
        "Devuelve totales de quejas para el rango/criterios seleccionados. "
        "Si se pasa `estado` (incluye múltiples, p.ej. `PEN,ENP`), los totales se limitan a ese subconjunto."
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                         description="Permite múltiples: `PEN,ENP,RES,REC`"),
        OpenApiParameter(name="categoria_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="distrito_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
    ],
    responses={200: OpenApiResponse(response=OverviewSerializer), 400: OpenApiResponse(description="Parámetro inválido")},
    examples=[
        OpenApiExample(
            "Ejemplo respuesta",
            value={"total": 287, "pen": 120, "enp": 65, "res": 90, "rec": 12},
            response_only=True,
        )
    ],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_overview(request):
    user_id = request.query_params.get("user_id")
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))
    if request.query_params.get("desde") and desde is None:
        return Response({"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400)
    if request.query_params.get("hasta") and hasta is None:
        return Response({"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400)

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    distrito_id = request.query_params.get("distrito_id")

    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if categoria_id:
        q &= Q(categoria_id=categoria_id)
    if distrito_id:
        q &= Q(distrito_id=distrito_id)
    if estados:
        q &= Q(estado__in=estados)

    agg = Queja.objects.filter(q).aggregate(
        total=Count("id"),
        pen=Count("id", filter=Q(estado="PEN")),
        enp=Count("id", filter=Q(estado="ENP")),
        res=Count("id", filter=Q(estado="RES")),
        rec=Count("id", filter=Q(estado="REC")),
    )
    # Asegurar enteros
    data = {k: int(agg.get(k, 0) or 0) for k in ("total", "pen", "enp", "res", "rec")}
    return Response(data)


# ============================================
# GET /stats/estados/ → conteo por estado
# ============================================
@extend_schema(
    summary="Distribución por estado",
    description=(
        "Devuelve conteos de quejas por estado. "
        "Si se pasa `estado` (múltiple permitido), la salida se limita a esos estados."
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                         description="Permite múltiples: `PEN,ENP,RES,REC`"),
        OpenApiParameter(name="categoria_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="distrito_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
    ],
    responses={200: OpenApiResponse(response=EstadosSerializer), 400: OpenApiResponse(description="Parámetro inválido")},
    examples=[OpenApiExample("Ejemplo respuesta", value={"PEN": 120, "ENP": 65, "RES": 90, "REC": 12, "total": 287})],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_estados(request):
    user_id = request.query_params.get("user_id")
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))
    if request.query_params.get("desde") and desde is None:
        return Response({"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400)
    if request.query_params.get("hasta") and hasta is None:
        return Response({"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400)

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    distrito_id = request.query_params.get("distrito_id")

    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if categoria_id:
        q &= Q(categoria_id=categoria_id)
    if distrito_id:
        q &= Q(distrito_id=distrito_id)
    if estados:
        q &= Q(estado__in=estados)

    base = Queja.objects.filter(q)
    data = {
        "PEN": base.filter(estado="PEN").count(),
        "ENP": base.filter(estado="ENP").count(),
        "RES": base.filter(estado="RES").count(),
        "REC": base.filter(estado="REC").count(),
    }
    data["total"] = sum(data.values())
    return Response(data)


# ============================================
# GET /stats/timeseries/ → serie temporal
# ============================================
@extend_schema(
    summary="Serie temporal de quejas",
    description=(
        "Devuelve puntos temporales agrupados por `group_by` y opcionalmente apilados por `estado`.\n\n"
        "`group_by`: `day | week | month | year` (por defecto `month`).\n"
        "`stack_by`: `none | estado` (por defecto `none`)."
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(name="group_by", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                         description="day | week | month | year"),
        OpenApiParameter(name="stack_by", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                         description="none | estado"),
        OpenApiParameter(name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                         description="Permite múltiples: `PEN,ENP,RES,REC`"),
        OpenApiParameter(name="categoria_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="distrito_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
    ],
    responses={200: OpenApiResponse(response=TimeSeriesPointSerializer(many=True)),
               400: OpenApiResponse(description="Parámetro inválido")},
    examples=[
        OpenApiExample(
            "Ejemplo mensual apilado por estado",
            value=[
                {"period": "2025-01", "total": 42, "by_estado": {"PEN": 20, "ENP": 10, "RES": 9, "REC": 3}},
                {"period": "2025-02", "total": 55, "by_estado": {"PEN": 22, "ENP": 14, "RES": 15, "REC": 4}}
            ],
            response_only=True,
        )
    ],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_timeseries(request):
    group_by = (request.query_params.get("group_by") or "month").lower()
    if group_by not in {"day", "week", "month", "year"}:
        return Response({"detail": "Parametro 'group_by' inválido. Use: day|week|month|year."}, status=400)

    stack_by = (request.query_params.get("stack_by") or "none").lower()
    if stack_by not in {"none", "estado"}:
        return Response({"detail": "Parametro 'stack_by' inválido. Use: none|estado."}, status=400)

    user_id = request.query_params.get("user_id")
    desde = _parse_date(request.query_params.get("desde"))
    hasta = _parse_date(request.query_params.get("hasta"))
    if request.query_params.get("desde") and desde is None:
        return Response({"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400)
    if request.query_params.get("hasta") and hasta is None:
        return Response({"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400)

    try:
        estados = _parse_estado_list(request.query_params.get("estado"))
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    distrito_id = request.query_params.get("distrito_id")

    # filtros
    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if categoria_id:
        q &= Q(categoria_id=categoria_id)
    if distrito_id:
        q &= Q(distrito_id=distrito_id)
    if estados:
        q &= Q(estado__in=estados)

    trunc_map = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth, "year": TruncYear}
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

    # Formateo de etiqueta 'period' según granularidad
    results = []
    for row in qs:
        dt = row["period_dt"]
        if group_by == "day":
            label = dt.strftime("%Y-%m-%d")
        elif group_by == "week":
            iso = dt.isocalendar()
            label = f"{iso.year}-W{iso.week:02d}"
        elif group_by == "month":
            label = dt.strftime("%Y-%m")
        else:  # year
            label = dt.strftime("%Y")

        item = {"period": label, "total": int(row["total"] or 0)}
        if stack_by == "estado":
            item["by_estado"] = {
                "PEN": int(row.get("PEN") or 0),
                "ENP": int(row.get("ENP") or 0),
                "RES": int(row.get("RES") or 0),
                "REC": int(row.get("REC") or 0),
            }
        results.append(item)

    return Response(results)