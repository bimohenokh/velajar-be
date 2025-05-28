from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .schemas import register_schema, login_schema, profile_schema
from .serializers import RegisterInSerializer, LoginInSerializer, UserSerializer, LoginOutSerializer
from taschoolassistant.core.utils.response import ApiResponse

User = get_user_model()


@register_schema
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return ApiResponse.success(
            data=UserSerializer(user).data,
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )


@login_schema
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=identifier).first(
        ) or User.objects.filter(username=identifier).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        refresh["username"] = user.username
        refresh["email"] = user.email
        refresh["nama_lengkap"] = user.nama_lengkap
        refresh["role"] = user.role

        return ApiResponse.success(
            data=LoginOutSerializer({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }).data,
            message="Login successful",
            status_code=status.HTTP_200_OK
        )


@profile_schema
class ProfileView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return ApiResponse.success(
            data=serializer.data,
            message="User profile retrieved successfully",
            status_code=status.HTTP_200_OK
        )
