from drf_spectacular.utils import extend_schema

from taschoolassistant.core.schemas import open_api_wrap, error_open_api_wrap
from taschoolassistant.courses.serializers import CourseSerializer

course_get_schema = extend_schema(
    request=CourseSerializer,
    responses={
        201: open_api_wrap(
            CourseSerializer,
            201,
            "Course succesfully retrieved"
        ),
    },
)

course_post_schema = extend_schema(
    request=CourseSerializer,
    responses={
        201: open_api_wrap(
            CourseSerializer,
            201, "Course successfully created"
        ),
        400: error_open_api_wrap(
            400,
            "Validation error",
            {
                "field": ["error message"]
            }
        ),
    },
)

course_by_id_get_schema = extend_schema(
    request=CourseSerializer,
    responses={
        201: open_api_wrap(
            CourseSerializer,
            200, "Course successfully retrieved"
        ),
        404: error_open_api_wrap(
            404,
            "Not found.",
            {
                "detail": "Course not found"
            }
        ),
    },
)

course_by_id_put_schema = extend_schema(
    request=CourseSerializer,
    responses={
        201: open_api_wrap(
            CourseSerializer,
            200, "Course successfully retrieved"
        ),
        400: error_open_api_wrap(
            400,
            "Validation error",
            {
                "field": ["error message"]
            }
        ),
        404: error_open_api_wrap(
            404,
            "Course not found.",
            {
                "detail": "Course not found"
            }
        ),
    },
)

course_by_id_delete_schema = extend_schema(
    responses={
        204: None,
        404: error_open_api_wrap(
            404,
            "Course not found.",
            {
                "detail": "Course not found"
            }
        ),
    },
    description="Delete a course by its ID."
)