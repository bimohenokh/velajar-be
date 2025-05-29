from copy import deepcopy

from rest_framework import status
from rest_framework.views import APIView
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from .serializers import ResourceSerializer, ResourceParamSerializer
from .models import Resource, ResourceType
from ..courses.models import CourseParticipant, CourseSession


# Create your views here.
class ResourceView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        request_param = ResourceParamSerializer(data=request.query_params)
        request_param.is_valid(raise_exception=True)

        course_session_id = request_param.data.get('course_session_id')

        resources = list(Resource.objects.filter(course_session_id=course_session_id))

        course_session = CourseSession.objects.get(id=course_session_id)
        # check if user is participant of the course
        try:
            participant = CourseParticipant.objects.get(participant=request.user, course_id=course_session.course_id)
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("Participant not found.")

        out_serializer = ResourceSerializer(resources, many=True)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Resources successfully retrieved",
            status_code=status.HTTP_200_OK
        )
    
    def post(self, request):
        param_serializer = ResourceParamSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)
        course_session_id = param_serializer.validated_data.get('course_session_id')

        course_session = CourseSession.objects.get(id=course_session_id)

        serializer = ResourceSerializer(
            data=request.data,
            context={'course_session': course_session},
            many=True
        )
        serializer.is_valid(raise_exception=True)

        # check if user is course instructor of the course
        try:
            participant = CourseParticipant.objects.get(
                participant=request.user, course_id=course_session.course_id, courseinstructor__isnull=False
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("Participant not allowed to create resources.")

        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Resources successfully created",
            status_code=status.HTTP_201_CREATED
        )

        
class ResourceViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, resource_id):
        try:
            resource_instance = Resource.objects.select_related("course_session").get(pk=resource_id)
        except Resource.DoesNotExist:
            raise NotFound("Resource not found.")

        course_id = resource_instance.course_session.course_id
        # check if user is participant of the course
        try:
            participant = CourseParticipant.objects.get(participant=request.user, course_id=course_id)
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("Participant not found.")

        serializer = ResourceSerializer(resource_instance)

        return ApiResponse.success(
            data=serializer.data,
            message="Resource successfully retrieved",
            status_code=status.HTTP_200_OK
        )

    def patch(self, request, resource_id):
        try:
            resource_instance = Resource.objects.select_related("course_session").get(pk=resource_id)
        except Resource.DoesNotExist:
            raise NotFound("Resource not found.")

        course_id = resource_instance.course_session.course_id
        # check if user is participant of the course
        try:
            participant = CourseParticipant.objects.get(
                participant=request.user, course_id=course_id, courseinstructor__isnull=False
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("Participant not found.")
        
        data = request.data

        if ((resource_instance.resource_type == ResourceType.FILE and data.get('file') is None) or
                (resource_instance.resource_type == ResourceType.LINK and data.get('link') is None)):
            raise ValidationError("Resource type mismatch.")
        
        serializer = ResourceSerializer(resource_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Resource successfully updated",
            status_code=status.HTTP_200_OK
        )
    
    def delete(self, request, resource_id):
        try:
            resource_instance = Resource.objects.select_related("course_session").get(
                pk=resource_id
            )
        except Resource.DoesNotExist:
            raise NotFound("Resource not found.")

        course_id = resource_instance.course_session.course_id
        # check if user is participant of the course
        try:
            participant = CourseParticipant.objects.get(
                participant=request.user, course_id=course_id, courseinstructor__isnull=False
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("Participant not found.")

        resource_instance.delete()

        return ApiResponse.success(
            message="Resource successfully deleted",
            status_code=status.HTTP_200_OK
        )