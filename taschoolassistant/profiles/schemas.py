from drf_spectacular.utils import extend_schema, extend_schema_view
from taschoolassistant.core.schemas import open_api_wrap, error_open_api_wrap
from .serializers import TeacherProfileSerializer, StudentProfileSerializer


# ✅ Helper to apply tags automatically
def with_tags(**schema_kwargs):
    """Automatically applies 'Profile' tag to extend_schema"""
    return extend_schema(**schema_kwargs)


# ✅ Reusable error responses
VALIDATION_ERROR = error_open_api_wrap(400, "Validation error", {"field": ["error message"]})
NOT_FOUND_ERROR = error_open_api_wrap(404, "Not found", {"detail": "Course not found"})

# ✅ Class-level schema decorator
profile_schema = extend_schema_view(
    get=with_tags(
        summary="Retrieve student profile",
        responses={
            200: open_api_wrap(StudentProfileSerializer, 200, "Student profile retrieved"),
            200: open_api_wrap(TeacherProfileSerializer, 200, "Teacher profile retrieved"),
            404: NOT_FOUND_ERROR,

        },
    ),
    patch=with_tags(
        summary="Update profile",
        request=[StudentProfileSerializer, TeacherProfileSerializer], description="Request body depends on user role",
        responses={
            200: open_api_wrap(StudentProfileSerializer, 200, "Student profile succesfully updated"),
            200: open_api_wrap(TeacherProfileSerializer, 200, "Teacher profile succesfully updated"),
            400: VALIDATION_ERROR
        },
    ),
)
