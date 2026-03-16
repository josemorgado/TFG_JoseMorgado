from django.urls import path
from stats.views import stats_categorias, stats_distritos
urlpatterns = [
    path("categorias/", stats_categorias, name="stats-categorias"),
    path("distritos/", stats_distritos, name="stats-distritos"),
]
