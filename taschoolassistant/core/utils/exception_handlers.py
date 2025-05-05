from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from taschoolassistant.core.serializers import StandardErrorOutSerializer


def custom_exception_handler(exc: APIException, context):
    """Customize all DRF error responses"""
    response = exception_handler(exc, context)

    # ✅ If response is None, it's a 500 error → Let Django handle it
    if response is None:
        return None

    # ✅ Customize only non-500 errors
    return Response(
        StandardErrorOutSerializer({
            "status": exc.status_code,
            "errors": exc.get_full_details(),
        }).data,
        status=exc.status_code
    )
