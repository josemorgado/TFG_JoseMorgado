from tokenize import Token
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

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

    # API de stats.
    path('api/stats/', include('stats.urls')),

    # Endpoint para obtener el par de tokens JWT (access + refresh)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Endpoint para renovar el token de acceso usando el refresh token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Esquema OpenAPI (JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger-UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)