from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data["status_code"] = response.status_code
    else:

        response = Response(
            {"message": exc.message, "errors": exc.errors, "data": exc.data},
            status=exc.status_code,
        )

    return response
