from rest_framework.views import APIView
from .models import Course, CourseParticipant, CourseInstructor
from .schemas import course_schema, course_by_id_schema
from .serializers import CourseSerializer
from rest_framework import status

from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError


@course_schema
class CourseView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_serializer = CourseSerializer

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


@course_by_id_schema
class CourseViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_serializer = CourseSerializer

    def get(self, request, pk=None):
        user = request.user
        course_instance = Course.objects.get_detail_course_by_id(user, pk)

        if not course_instance:
            raise NotFound("Course not found")

        serializer = self.course_serializer(course_instance)
        return ApiResponse.success(serializer.data, message="Course successfully retrieved")

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
