from django.shortcuts import render
from rest_framework.views import APIView
from .models import Course, CourseParticipant, CourseInstructor
from .serializers import CourseSerializer
from rest_framework import status
from ..utils.response import ApiResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


# Create your views here.

class CourseReadView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        self.course_serializer = CourseSerializer

    def get(self, request):
        try:
            user = request.user
            name = request.GET.get('name', None)
            jenjang = request.GET.get('jenjang_kelas', None)
            courses_instance = Course.objects.get_courses(user, name, jenjang)
            if not courses_instance.exists():
                return ApiResponse.error(message="Courses empty", status_code=status.HTTP_404_NOT_FOUND)
            serializer = self.course_serializer(
                courses_instance, many=True)

            return ApiResponse.success(serializer.data, message="Course succesfully retrieved")

        except Exception as e:
            return ApiResponse.error(message=str(e))


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            user = request.user
            course_instance = Course.objects.get_detail_course_by_id(user, pk)

            if not course_instance:
                return ApiResponse.error(message="Course not found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = CourseSerializer(course_instance)
            return ApiResponse.success(serializer.data, message="Course successfully retrieved")

        except Course.DoesNotExist:
            return ApiResponse.error(message="Course not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponse.error(message=str(e))


class CoursePostView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            user = request.user
            role = user.role
            serializer = CourseSerializer(data=request.data)

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
                return ApiResponse.error(
                    message="Serializer isn't valid",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return ApiResponse.error(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        try:
            user = request.user
            try:
                selected_course = Course.objects.get(pk=pk)
            except Course.DoesNotExist:
                return ApiResponse.error(
                    message="Course not found"
                )
            request_data = request.data

            serializer = CourseSerializer(
                selected_course, data=request_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    data=serializer.data,
                    message="Course successfully updated"
                )
            else:
                return ApiResponse.error(
                    message="Invalid data",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return ApiResponse.error(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
        except Course.DoesNotExist:
            return ApiResponse.error(
                message="Course not found"
            )

        course.delete()
        return ApiResponse.success(
            message="Course successfully deleted",
            status_code=status.HTTP_204_NO_CONTENT
        )
