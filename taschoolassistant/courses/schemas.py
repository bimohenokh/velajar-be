from drf_spectacular.utils import extend_schema, extend_schema_view
from taschoolassistant.core.schemas import open_api_wrap, error_open_api_wrap
from .serializers import CourseSerializer


# ✅ Helper to apply tags automatically
def with_tags(**schema_kwargs):
    """Automatically applies 'Courses' tag to extend_schema"""
    return extend_schema(**schema_kwargs)


# ✅ Reusable error responses
VALIDATION_ERROR = error_open_api_wrap(400, "Validation error", {"field": ["error message"]})
NOT_FOUND_ERROR = error_open_api_wrap(404, "Not found", {"detail": "Course not found"})

# ✅ Class-level schema decorator
course_schema = extend_schema_view(
    get=with_tags(
        summary="Retrieve all courses",
        responses={
            200: open_api_wrap(CourseSerializer, 200, "Courses retrieved")
        },
    ),
    post=with_tags(
        summary="Create a course",
        request=CourseSerializer,
        responses={
            201: open_api_wrap(CourseSerializer, 201, "Course successfully created"),
            400: VALIDATION_ERROR
        },
    ),
)

course_by_id_schema = extend_schema_view(
    get=with_tags(
        summary="Retrieve a course by ID",
        responses={
            200: open_api_wrap(CourseSerializer, 200, "Course retrieved"),
            404: NOT_FOUND_ERROR
        },
    ),
    put=with_tags(
        summary="Update a course",
        request=CourseSerializer,
        responses={
            200: open_api_wrap(CourseSerializer, 200, "Course updated"),
            400: VALIDATION_ERROR,
            404: NOT_FOUND_ERROR
        },
    ),
    delete=with_tags(
        summary="Delete a course",
        responses={
            204: None,
            404: NOT_FOUND_ERROR
        },
    ),
)
