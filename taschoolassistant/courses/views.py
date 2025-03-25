from django.shortcuts import render
from rest_framework.views import APIView
from .models import Course
from .serializers import CourseSerializer
from rest_framework import status
from ..utils.response import ApiResponse


# Create your views here.

class CourseView(APIView):

    def __init__(self):
        self.course_serializer = CourseSerializer

    def get(self, request, pk=None):
        try:
            if pk:
                course_instance = Course.objects.read_by_id(pk)
                if course_instance:
                    serializer = self.course_serializer(course_instance)
                else:
                    return ApiResponse.error(message="No course found", status_code=status.HTTP_404_NOT_FOUND)
            else:
                courses_instance = Course.objects.read_all()
                if not courses_instance.exists():
                    return ApiResponse.error(message="Courses empty", status_code=status.HTTP_404_NOT_FOUND)
                serializer = self.course_serializer(
                    courses_instance, many=True)

            return ApiResponse.success(serializer.data, message="Course succesfully retrieved")

        except Exception as e:
            return ApiResponse.error(message=str(e))

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ApiResponse.success(serializer.data, message="Course succesfully created", status=status.HTTP_201_CREATED)
        return ApiResponse.error(error="Bad request when post")
