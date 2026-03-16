from django.urls import path
from stats.views import CategoriasMasUsadasView, DistritosMasUsadosView
urlpatterns = [
    path("categorias/", CategoriasMasUsadasView.as_view(), name="stats-categorias"),
    path("distritos/", DistritosMasUsadosView.as_view(), name="stats-distritos"),
]
