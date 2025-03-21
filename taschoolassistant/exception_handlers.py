from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Customize all DRF error responses"""
    response = exception_handler(exc, context)

    # ✅ If response is None, it's a 500 error → Let Django handle it
    if response is None:
        return None

    # ✅ Customize only non-500 errors
    response.data = {
        "status_code": response.status_code,
        "error": response.data,  # Keep original error messages
    }

    return response
