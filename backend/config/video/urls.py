# video/urls.py
from django.urls import path
from .views import (
    video_list,
    video_detail,
    videos_por_comentario,
    videos_por_queja,
    video_create,   # POST
    video_delete,   # DELETE
)

urlpatterns = [
    path('', video_list, name='video-list'),                                   # GET    /videos/
    path('<int:pk>/', video_detail, name='video-detail'),                      # GET    /videos/<pk>/
    path('queja/<int:queja_id>/', videos_por_queja, name='videos-por-queja'),  # GET    /videos/queja/<id>/
    path('comentario/<int:comentario_id>/', videos_por_comentario,             # GET    /videos/comentario/<id>/
         name='videos-por-comentario'),
    path('create/', video_create, name='video-create'),                         # POST   /videos/create/
    path('<int:pk>/delete/', video_delete, name='video-delete'),               # DELETE /videos/<pk>/delete/
]