from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # GET               /usuarios/
    path('', views.usuario_list, name='usuario-list'),

    # GET               /usuarios/<int:pk>/
    path('<int:pk>/', views.usuario_detail, name='usuario-detail'),

    # POST              /usuarios/create/
    path('create/', views.usuario_create, name='usuario-create'),

    # PUT               /usuarios/<int:pk>/update/
    path('<int:pk>/update/', views.usuario_update, name='usuario-update'),

    # PATCH             /usuarios/<int:pk>/partial-update/
    path('<int:pk>/partial-update/', views.usuario_partial_update, name='usuario-partial-update'),

    # DELETE            /usuarios/<int:pk>/delete/
    path('<int:pk>/delete/', views.usuario_delete, name='usuario-delete'),

    # GET/PATCH/PUT     /usuarios/me/
    path('me/', views.usuario_me, name='usuario-me'),

    # GET               /usuarios/<int:user_id>/imagenes/
    path('<int:user_id>/imagenes/', views.imagenes_de_usuario, name='usuario-imagenes'),

    # GET               /usuarios/me/imagenes/
    path('me/imagenes/', views.mis_imagenes, name='usuario-me-imagenes'),

    # GET               /usuarios/<int:user_id>/videos/
    path('<int:user_id>/videos/', views.videos_de_usuario, name='usuario-videos'),

    # GET               /usuarios/me/videos/
    path('me/videos/', views.mis_videos, name='usuario-me-videos'),

    #POST              /usuarios/logout/
    path('logout/', views.logout_view, name='usuario-logout'),

    #PATCH              /usuarios/<int:user_id>/change-password
    path('<int:pk>/change-password/', views.change_password, name='usuario-change-password'),
]