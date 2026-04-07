# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/quejas/', include('quejas.urls')),
    path('api/categorias/', include('categoria.urls')),
    path('api/distritos/', include('distrito.urls')),
    path('api/comentarios/', include('comentario.urls')),
    path('api/imagenes/', include('imagen.urls')),
    path('api/videos/', include('video.urls')),
    path('api/megusta/', include('megusta.urls')),
    path('api/usuarios/', include('perfil.urls')),
    path('api/suggestions/', include('suggestion.urls')),

    path('api/', include('respuesta.urls')),

    path('api/stats/', include('stats.urls')),
    path('api/notificaciones/', include('notificaciones.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)