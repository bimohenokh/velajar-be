from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, ValidationError
from .serializers import StudentProfileSerializer, TeacherProfileSerializer, StudentPostProfileSerializer, TeacherPostProfileSerializer
from .models import StudentProfile, TeacherProfile
from .schemas import profile_schema
from taschoolassistant.users.models import User

# Create your views here.

@profile_schema
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request):
        user = request.user
        role = request.user.role

        profile_instance = TeacherProfile.objects.get_profile(user) if role == "teacher" else StudentProfile.objects.get_profile(user)
        if not profile_instance:
            raise NotFound("Profile not found")
        
        serializer = TeacherProfileSerializer(profile_instance) if role == "teacher" else StudentProfileSerializer(profile_instance)

        return ApiResponse.success(
            data=serializer.data,
            message="Profile succesfully retrieved"
        )

    def patch(self, request):
        user = request.user
        role = request.user.role

        profile_instance = TeacherProfile.objects.get_profile(user) if role == "teacher" else StudentProfile.objects.get_profile(user)
        if not profile_instance:
            raise NotFound("Profile not found")

        serializer = TeacherProfileSerializer(profile_instance, request.data, partial=True)  if role == "teacher" else StudentProfileSerializer(profile_instance, request.data, partial=True) 
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Profile successfully updated",
            status_code=status.HTTP_200_OK
        )

class ProfilePostView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        role = user.role
        data = request.data.copy()  

        serializer = StudentPostProfileSerializer(data=data, context={"user": user}) if role == "student" else TeacherPostProfileSerializer(data=data, context={"user": user}) 
    
        if serializer.is_valid():
            serializer.save()
            return ApiResponse.success(
                data=serializer.data,
                message="Profile successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError("Invalid input data type")



        

    


