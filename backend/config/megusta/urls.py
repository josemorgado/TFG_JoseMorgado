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
    path('', megusta_list),                               # GET /megusta/
    path('<int:pk>/', megusta_detail),                    # GET /megusta/<pk>/
    path('queja/<int:queja_id>/', megusta_por_queja),     # GET /megusta/queja/<id>/
    path('comentario/<int:comentario_id>/', megusta_por_comentario), # GET /megusta/comentario/<id>/
    path('toggle/', megusta_toggle),                      # POST /megusta/toggle/
    path('<int:pk>/delete/', megusta_delete),             # DELETE /megusta/<pk>/delete/
]