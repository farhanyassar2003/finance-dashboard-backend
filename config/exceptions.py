from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data

        if isinstance(errors, dict) and "detail" in errors:
            detail = errors.get("detail")
            if not isinstance(detail, list):
                detail = [str(detail)]

            errors = {
                "non_field_errors": detail
            }

        return Response(
            {
                "message": "Request failed.",
                "errors": errors,
            },
            status=response.status_code,
        )

    return Response(
        {
            "message": "Internal server error.",
            "errors": {
                "non_field_errors": ["Something went wrong on the server."]
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )