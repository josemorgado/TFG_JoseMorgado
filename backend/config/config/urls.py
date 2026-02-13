from django.contrib import admin
from django.urls import include, path

# Rutas globales del proyecto. Cada prefijo /api/... delega en el archivo urls.py de su app correspondiente.
urlpatterns = [
    # Administración de Django.
    path('admin/', admin.site.urls),

    # API de gestión de quejas.
    path('api/quejas/', include('quejas.urls')),

    # API de categorías asociadas a las quejas.
    path('api/categorias/', include('categoria.urls')),

    # API de distritos (zonas geográficas).
    path('api/distritos/', include('distrito.urls')),

    # API de comentarios y respuestas de usuarios.
    path('api/comentarios/', include('comentario.urls')),

    # API de imágenes asociadas a las quejas.
    path('api/imagenes/', include('imagen.urls')),

    # API de vídeos asociados a las quejas.
    path('api/videos/', include('video.urls')),

    # API de votos ("me gusta") para comentarios y quejas.
    path('api/megusta/', include('megusta.urls')),

    # API de usuarios y perfiles.
    path('api/usuarios/', include('perfil.urls')),
]