from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, ValidationError
from .serializers import ResourceSerializer
from .models import Resource

# Create your views here.
class ResourceView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_serializer = ResourceSerializer

    def get(self, request, session_id):
        user = request.user

        resources_instance = Resource.objects.get_resources(user, session_id)
        if not resources_instance:
            raise NotFound("Resources not found")
        
        serializer = self.resource_serializer(resources_instance, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Resources succesfully retrieved"
        )
    
    def post(self, request, session_id):
        incoming_data = request.data

        if isinstance(incoming_data, list):
            for item in incoming_data:
                item['course_session'] = session_id
        else:
            incoming_data['course_session'] = session_id

        many = isinstance(incoming_data, list)
        serializer = self.resource_serializer(data=incoming_data, many=many)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse.success(
                data=serializer.data,
                message="Resources successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError(serializer.errors)
        
class ResourceViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_serializer = ResourceSerializer

    def patch(self, request, session_id, resource_id):
        user = request.user
        try:
            resource_instance = Resource.objects.get(course_session=session_id, pk=resource_id)
        except Resource.DoesNotExist:
            raise NotFound("Resource not found.")
        
        data = request.data
        print(data["resource_type"])
        if data["resource_type"] == "File":
            resource_instance.link = None
        else:
            resource_instance.file = None
        
        serializer = self.resource_serializer(resource_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Resource successfully updated",
            status_code=status.HTTP_200_OK
        )
    
    def delete(self, request, session_id, resource_id):
        try:
            resource_instance = Resource.objects.get(course_session=session_id, pk=resource_id)
        except Resource.DoesNotExist:
            raise NotFound("Course session not found.")

        resource_instance.delete()

        return ApiResponse.success(
            message="Resource successfully deleted",
            status_code=status.HTTP_204_NO_CONTENT
        )