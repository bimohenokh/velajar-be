from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from taschoolassistant.utils.response import ApiResponse


def custom_exception_handler(exc: APIException, context):
    """Customize all DRF error responses"""
    response = exception_handler(exc, context)

    # ✅ If response is None, it's a 500 error → Let Django handle it
    if response is None:
        return None

    # ✅ Customize only non-500 errors
    return ApiResponse.error(
        message=exc.default_detail,
        status_code=response.status_code,
        errors=response.data
    )
