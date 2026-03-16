# stats/views.py
from datetime import datetime
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers

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


def _parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "t", "yes", "y")


# ----------------------------
# Serializers simples para documentación de respuesta
# ----------------------------
class StatItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    total = serializers.IntegerField()


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
        "- `estado`: `PEN|ENP|RES|REC`\n"
        "- `distrito_id`: int\n"
        "- `include_zero`: bool (incluir categorías sin ninguna queja)\n"
        "- `ordering`: `-total` (default) | `total` | `nombre`"
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="limit", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Número de resultados (default 5)"),
        OpenApiParameter(name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Uno de PEN, ENP, RES, REC"),
        OpenApiParameter(name="distrito_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="include_zero", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="ordering", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="`-total` (default) | `total` | `nombre`"),
    ],
    responses={
        200: OpenApiResponse(response=StatItemSerializer(many=True)),
        400: OpenApiResponse(description="Parámetro inválido"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo básico",
            value=[{"id": 3, "nombre": "Vía pública", "total": 42},
                   {"id": 1, "nombre": "Limpieza", "total": 27}],
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
        return Response({"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400)
    if request.query_params.get("hasta") and hasta is None:
        return Response({"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400)

    estado = request.query_params.get("estado")
    if estado and estado not in ("PEN", "ENP", "RES", "REC"):
        return Response({"detail": "Parametro 'estado' inválido. Use PEN, ENP, RES o REC."}, status=400)

    distrito_id = request.query_params.get("distrito_id")
    include_zero = _parse_bool(request.query_params.get("include_zero"), default=False)
    ordering = request.query_params.get("ordering", "-total")
    if ordering not in ("-total", "total", "nombre"):
        return Response({"detail": "Parametro 'ordering' inválido. Use '-total', 'total' o 'nombre'."}, status=400)

    # --- filtros para consultas basadas en Queja
    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if estado:
        q &= Q(estado=estado)
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
        if estado:
            q_rel &= Q(quejas__estado=estado)
        if distrito_id:
            q_rel &= Q(quejas__distrito_id=distrito_id)

        qs = (
            Categoria.objects.values("id", "nombre")
            .annotate(total=Count("quejas", filter=q_rel))
        )
        if ordering == "nombre":
            qs = qs.order_by("nombre")
        elif ordering == "total":
            qs = qs.order_by("total")
        else:
            qs = qs.order_by("-total")
        if limit:
            qs = qs[:limit]

        data = [{"id": row["id"], "nombre": row["nombre"], "total": row["total"] or 0} for row in qs]
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
            {"id": row["categoria_id"], "nombre": row["categoria__nombre"], "total": row["total"]}
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
        "- `estado`: `PEN|ENP|RES|REC`\n"
        "- `categoria_id`: int\n"
        "- `include_zero`: bool (incluir distritos sin ninguna queja)\n"
        "- `ordering`: `-total` (default) | `total` | `nombre`"
    ),
    tags=["Estadísticas"],
    parameters=[
        OpenApiParameter(name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="limit", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Número de resultados (default 5)"),
        OpenApiParameter(name="desde", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="hasta", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Uno de PEN, ENP, RES, REC"),
        OpenApiParameter(name="categoria_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="include_zero", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="ordering", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="`-total` (default) | `total` | `nombre`"),
    ],
    responses={
        200: OpenApiResponse(response=StatItemSerializer(many=True)),
        400: OpenApiResponse(description="Parámetro inválido"),
    },
    examples=[
        OpenApiExample(
            "Ejemplo básico",
            value=[{"id": 1, "nombre": "Centro", "total": 35},
                   {"id": 2, "nombre": "Norte", "total": 18}],
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
        return Response({"detail": "Parametro 'desde' debe tener formato YYYY-MM-DD."}, status=400)
    if request.query_params.get("hasta") and hasta is None:
        return Response({"detail": "Parametro 'hasta' debe tener formato YYYY-MM-DD."}, status=400)

    estado = request.query_params.get("estado")
    if estado and estado not in ("PEN", "ENP", "RES", "REC"):
        return Response({"detail": "Parametro 'estado' inválido. Use PEN, ENP, RES o REC."}, status=400)

    categoria_id = request.query_params.get("categoria_id")
    include_zero = _parse_bool(request.query_params.get("include_zero"), default=False)
    ordering = request.query_params.get("ordering", "-total")
    if ordering not in ("-total", "total", "nombre"):
        return Response({"detail": "Parametro 'ordering' inválido. Use '-total', 'total' o 'nombre'."}, status=400)

    # --- filtros para consultas basadas en Queja
    q = Q()
    if user_id:
        q &= Q(autor_id=user_id)
    if desde:
        q &= Q(fecha_creacion__date__gte=desde)
    if hasta:
        q &= Q(fecha_creacion__date__lte=hasta)
    if estado:
        q &= Q(estado=estado)
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
        if estado:
            q_rel &= Q(quejas__estado=estado)
        if categoria_id:
            q_rel &= Q(quejas__categoria_id=categoria_id)

        qs = (
            Distrito.objects.values("id", "nombre")
            .annotate(total=Count("quejas", filter=q_rel))
        )
        if ordering == "nombre":
            qs = qs.order_by("nombre")
        elif ordering == "total":
            qs = qs.order_by("total")
        else:
            qs = qs.order_by("-total")
        if limit:
            qs = qs[:limit]

        data = [{"id": row["id"], "nombre": row["nombre"], "total": row["total"] or 0} for row in qs]
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
            {"id": row["distrito_id"], "nombre": row["distrito__nombre"], "total": row["total"]}
            for row in qs
        ]

    return Response(data)