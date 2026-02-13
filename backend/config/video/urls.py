from django.urls import path
from .views import (
    video_list,
    video_detail,
    videos_por_comentario,
    videos_por_queja,
    video_create,
    video_delete,
)

urlpatterns = [
    # GET               /videos/
    path('', video_list, name='video-list'),

    # GET               /videos/<int:pk>/
    path('<int:pk>/', video_detail, name='video-detail'),

    # GET               /videos/queja/<int:queja_id>/
    path('queja/<int:queja_id>/', videos_por_queja, name='videos-por-queja'),

    # GET               /videos/comentario/<int:comentario_id>/
    path('comentario/<int:comentario_id>/', videos_por_comentario, name='videos-por-comentario'),

    # POST              /videos/create/
    path('create/', video_create, name='video-create'),

    # DELETE            /videos/<int:pk>/delete/
    path('<int:pk>/delete/', video_delete, name='video-delete'),
]