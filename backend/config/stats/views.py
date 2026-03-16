from datetime import datetime
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from quejas.models import Queja
from categoria.models import Categoria
from distrito.models import Distrito


def _parse_date(value):
    """Devuelve date o None si es inválida."""
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


class CategoriasMasUsadasView(APIView):
    """
    Devuelve las categorías más usadas (global o por usuario).
    Parámetros soportados (querystring):
      - user_id: int
      - limit: int (por defecto 5)
      - desde: YYYY-MM-DD
      - hasta: YYYY-MM-DD
      - estado: PEN|ENP|RES|REC
      - distrito_id: int (para limitar al distrito X)
      - include_zero: bool (incluir categorías sin quejas)
      - ordering: '-total' (default) | 'total' | 'nombre'
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # --- lectura de parámetros
        user_id = request.query_params.get("user_id")
        try:
            limit = int(request.query_params.get("limit", 5))
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
            # Cuando queremos incluir categorías sin quejas, partimos de Categoria y anotamos el count
            # Usamos un Q(*) equivalente con prefijo 'quejas__' (related_name en FK Queja.categoria)
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

            qs = (Categoria.objects
                  .values("id", "nombre")
                  .annotate(total=Count("quejas", filter=q_rel)))
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
            qs = (Queja.objects
                  .filter(q)
                  .values("categoria_id", "categoria__nombre")
                  .annotate(total=Count("id")))
            if ordering == "nombre":
                qs = qs.order_by("categoria__nombre")
            elif ordering == "total":
                qs = qs.order_by("total")
            else:
                qs = qs.order_by("-total")
            if limit:
                qs = qs[:limit]

            data = [{"id": row["categoria_id"], "nombre": row["categoria__nombre"], "total": row["total"]} for row in qs]

        return Response(data)


class DistritosMasUsadosView(APIView):
    """
    Devuelve los distritos más usados (global o por usuario).
    Parámetros soportados (querystring):
      - user_id: int
      - limit: int (por defecto 5)
      - desde: YYYY-MM-DD
      - hasta: YYYY-MM-DD
      - estado: PEN|ENP|RES|REC
      - categoria_id: int (para limitar a la categoría X)
      - include_zero: bool (incluir distritos sin quejas)
      - ordering: '-total' (default) | 'total' | 'nombre'
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # --- lectura de parámetros
        user_id = request.query_params.get("user_id")
        try:
            limit = int(request.query_params.get("limit", 5))
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
            # Partimos de Distrito y anotamos el count de quejas relacionadas
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

            qs = (Distrito.objects
                  .values("id", "nombre")
                  .annotate(total=Count("quejas", filter=q_rel)))
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
            qs = (Queja.objects
                  .filter(q)
                  .values("distrito_id", "distrito__nombre")
                  .annotate(total=Count("id")))
            if ordering == "nombre":
                qs = qs.order_by("distrito__nombre")
            elif ordering == "total":
                qs = qs.order_by("total")
            else:
                qs = qs.order_by("-total")
            if limit:
                qs = qs[:limit]

            data = [{"id": row["distrito_id"], "nombre": row["distrito__nombre"], "total": row["total"]} for row in qs]

        return Response(data)
