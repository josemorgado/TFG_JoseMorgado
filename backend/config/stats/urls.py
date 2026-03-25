from django.urls import path
from stats.views import (
    stats_categorias,
    stats_distritos,
    stats_estados,
    stats_overview,
    stats_timeseries,
    stats_respuestas_categorias,
    stats_respuestas_distritos,
    stats_respuestas_overview,
    stats_respuestas_timeseries,
)

urlpatterns = [
    path("categorias/", stats_categorias, name="stats-categorias"),
    path("distritos/", stats_distritos, name="stats-distritos"),
    path("overview/", stats_overview, name="stats-overview"),
    path("estados/", stats_estados, name="stats-estados"),
    path("timeseries/", stats_timeseries, name="stats-timeseries"),
    path("respuestas/overview/", stats_respuestas_overview),
    path("respuestas/timeseries/", stats_respuestas_timeseries),
    path("respuestas/categorias/", stats_respuestas_categorias),
    path("respuestas/distritos/", stats_respuestas_distritos),
]
