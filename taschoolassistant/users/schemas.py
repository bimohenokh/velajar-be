from drf_spectacular.utils import extend_schema

from taschoolassistant.core.schemas import open_api_wrap, error_open_api_wrap
from taschoolassistant.users.serializers import RegisterInSerializer, UserSerializer, LoginInSerializer, \
    LoginOutSerializer

register_post_schema = extend_schema(
    request=RegisterInSerializer,
    responses={
        201: open_api_wrap(UserSerializer, 201, "User registered successfully"),
        400: error_open_api_wrap(
            400,
            "Validation error",
            {
                "field": ["error message"]
            }
        ),
    }
)

login_post_schema = extend_schema(
    request=LoginInSerializer,
    responses={
        200: open_api_wrap(
            LoginOutSerializer,
            200,
            "Login Successful"
        ),
        401: error_open_api_wrap(
            401,
            "Invalid credentials",
            {
                "detail": "Invalid credentials"
            }
        ),
    },
)


profile_get_schema = extend_schema(
    responses={
        200: open_api_wrap(
            UserSerializer,
            200,
            "User profile retrieved successfully"
        ),
    },
)

