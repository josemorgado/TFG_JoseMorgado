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
]