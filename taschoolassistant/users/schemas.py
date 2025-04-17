from drf_spectacular.utils import extend_schema, extend_schema_view
from taschoolassistant.core.schemas import open_api_wrap, error_open_api_wrap
from .serializers import RegisterInSerializer, UserSerializer, LoginInSerializer, LoginOutSerializer


# ✅ Helper to apply the "Users" tag automatically
def with_tags(**schema_kwargs):
    return extend_schema(**schema_kwargs)


# ✅ Reusable error responses
VALIDATION_ERROR = error_open_api_wrap(400, "Validation error", {"field": ["error message"]})
INVALID_CREDENTIALS = error_open_api_wrap(401, "Invalid credentials", {"detail": "Invalid credentials"})

# ✅ Class-level schema decorator
register_schema = extend_schema_view(
    post=with_tags(
        summary="Register a new user",
        request=RegisterInSerializer,
        responses={
            201: open_api_wrap(UserSerializer, 201, "User registered successfully"),
            400: VALIDATION_ERROR
        },
    ),
)

login_schema = extend_schema_view(
    post=with_tags(
        summary="Login user",
        request=LoginInSerializer,
        responses={
            200: open_api_wrap(LoginOutSerializer, 200, "Login Successful"),
            401: INVALID_CREDENTIALS
        },
    ),
)

profile_schema = extend_schema_view(
    get=with_tags(
        summary="Retrieve user profile",
        responses={
            200: open_api_wrap(UserSerializer, 200, "User profile retrieved successfully")
        },
    ),
)
