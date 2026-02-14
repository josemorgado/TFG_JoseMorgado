# megusta/urls.py
from django.urls import path
from .views import (
    megusta_list,
    megusta_detail,
    megusta_por_queja,
    megusta_por_comentario,
    megusta_toggle,
    megusta_delete,
)

urlpatterns = [
    # GET               /megusta/
    path('', megusta_list, name='megusta-list'),

    # GET               /megusta/<int:pk>/
    path('<int:pk>/', megusta_detail, name='megusta-detail'),

    # GET               /megusta/queja/<int:queja_id>/
    path('queja/<int:queja_id>/', megusta_por_queja, name='megusta-por-queja'),

    # GET               /megusta/comentario/<int:comentario_id>/
    path('comentario/<int:comentario_id>/', megusta_por_comentario, name='megusta-por-comentario'),

    # POST              /megusta/toggle/
    path('toggle/', megusta_toggle, name='megusta-toggle'),

    # DELETE            /megusta/<int:pk>/delete/
    path('<int:pk>/delete/', megusta_delete, name='megusta-delete'),
]