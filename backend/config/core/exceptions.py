from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.db import IntegrityError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail")
        response.data = {
            "error": {
                "message": detail if isinstance(detail, str) else "La operación no se ha podido completar",
                "details": response.data
            }
        }
        return response

    if isinstance(exc, IntegrityError):
        return Response(
            {
                "error": {
                    "message": "Los datos introducidos no son válidos",
                    "details": None
                }
            },
            status=400
        )

    return Response(
        {
            "error": {
                "message": "Se ha producido un error interno",
                "details": None
            }
        },
        status=500
    )