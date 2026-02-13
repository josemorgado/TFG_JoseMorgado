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
    path('', megusta_list),

    # GET               /megusta/<int:pk>/
    path('<int:pk>/', megusta_detail),

    # GET               /megusta/queja/<int:queja_id>/
    path('queja/<int:queja_id>/', megusta_por_queja),

    # GET               /megusta/comentario/<int:comentario_id>/
    path('comentario/<int:comentario_id>/', megusta_por_comentario),

    # POST              /megusta/toggle/
    path('toggle/', megusta_toggle),

    # DELETE            /megusta/<int:pk>/delete/
    path('<int:pk>/delete/', megusta_delete),
]