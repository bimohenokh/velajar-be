from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from .models import Course, CourseParticipant, CourseInstructor
from .serializers import CourseSerializer
from rest_framework import status

from ..core.serializers import StandardOutSerializer, StandardErrorOutSerializer
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError


class CourseView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_serializer = CourseSerializer

    @extend_schema(
        request=CourseSerializer,
        responses={
            201: StandardOutSerializer.open_api_wrap(
                CourseSerializer,
                201,
                "Course succesfully retrieved"
            ),
        },
    )
    def get(self, request):
        user = request.user
        name = request.GET.get('name', None)
        jenjang = request.GET.get('jenjang_kelas', None)
        courses_instance = Course.objects.get_courses(user, name, jenjang)  # TODO kalau gk ada return kosong aja gk sih?
        if not courses_instance.exists():
            raise NotFound("Course not found")
        serializer = self.course_serializer(
            courses_instance, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Course succesfully retrieved"
        )

    @extend_schema(
        request=CourseSerializer,
        responses={
            201: StandardOutSerializer.open_api_wrap(
                CourseSerializer,
                201, "Course successfully created"
            ),
            400: StandardErrorOutSerializer.open_api_wrap(
                400,
                "Validation error",
                {
                    "field": ["error message"]
                }
            ),
        },
    )
    def post(self, request):
        user = request.user
        role = user.role
        serializer = self.course_serializer(data=request.data)

        if serializer.is_valid():
            course = serializer.save()

            course_participant = CourseParticipant.objects.create(
                course=course, participant=user, is_participating=True
            )

            if role == "teacher":
                CourseInstructor.objects.create(
                    course_participant=course_participant, is_owner=True
                )
            else:
                CourseInstructor.objects.create(
                    course_participant=course_participant, is_owner=False
                )

            return ApiResponse.success(
                data=serializer.data,
                message="Course successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError("Invalid input data type")


class CourseViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_serializer = CourseSerializer

    @extend_schema(
        request=CourseSerializer,
        responses={
            201: StandardOutSerializer.open_api_wrap(
                CourseSerializer,
                200, "Course successfully retrieved"
            ),
            404: StandardErrorOutSerializer.open_api_wrap(
                404,
                "Not found.",
                {
                    "detail": "Course not found"
                }
            ),
        },
    )
    def get(self, request, pk=None):
        user = request.user
        course_instance = Course.objects.get_detail_course_by_id(user, pk)

        if not course_instance:
            raise NotFound("Course not found")

        serializer = self.course_serializer(course_instance)
        return ApiResponse.success(serializer.data, message="Course successfully retrieved")

    @extend_schema(
        request=CourseSerializer,
        responses={
            201: StandardOutSerializer.open_api_wrap(
                CourseSerializer,
                200, "Course successfully retrieved"
            ),
            400: StandardErrorOutSerializer.open_api_wrap(
                400,
                "Validation error",
                {
                    "field": ["error message"]
                }
            ),
            404: StandardErrorOutSerializer.open_api_wrap(
                404,
                "Course not found.",
                {
                    "detail": "Course not found"
                }
            ),
        },
    )
    def put(self, request, pk=None):
        try:
            selected_course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise NotFound("Course not found.")

        serializer = self.course_serializer(selected_course, request.data, partial=True)  # TODO jadinya http patch?
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Course successfully updated",
            status_code=status.HTTP_200_OK
        )

    @extend_schema(
        responses={
            204: None,
            404: StandardErrorOutSerializer.open_api_wrap(
                404,
                "Course not found.",
                {
                    "detail": "Course not found"
                }
            ),
        },
        description="Delete a course by its ID."
    )
    def delete(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
        except Course.DoesNotExist:
            raise NotFound("Course not found")
        course.delete()
        return ApiResponse.success(
            message="Course successfully deleted",
            status_code=status.HTTP_204_NO_CONTENT
        )
