from rest_framework.response import Response
from rest_framework.views import exception_handler

from taschoolassistant.core.serializers import StandardErrorOutSerializer


def custom_exception_handler(exc, context):
    """Customize all DRF error responses"""
    response = exception_handler(exc, context)

    # ✅ If response is None, it's a 500 error → Let Django handle it
    if response is None:
        return None

    # ✅ Customize only non-500 errors
    return Response(
        StandardErrorOutSerializer({
            "status": response.status_code,
            "errors": response.data,
        }).data,
        status=response.status_code
    )
