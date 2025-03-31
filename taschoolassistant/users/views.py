from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterInSerializer, LoginInSerializer, UserSerializer, LoginOutSerializer
from ..core.serializers import StandardOutSerializer, StandardErrorOutSerializer
from taschoolassistant.core.utils.response import ApiResponse

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterInSerializer,
        responses={
            201: StandardOutSerializer.open_api_wrap(UserSerializer, 201, "User registered successfully"),
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
        serializer = RegisterInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return ApiResponse.success(
            data=UserSerializer(user).data,
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginInSerializer,
        responses={
            200: StandardOutSerializer.open_api_wrap(
                LoginOutSerializer,
                200,
                "Login Successful"
            ),
            401: StandardErrorOutSerializer.open_api_wrap(
                401,
                "Invalid credentials",
                {
                    "detail": "Invalid credentials"
                }
            ),
        },
    )
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

        return ApiResponse.success(
            data=LoginOutSerializer({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            }).data,
            message="Login successful",
            status_code=status.HTTP_200_OK
        )


class ProfileView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: StandardOutSerializer.open_api_wrap(
                serializer_class,
                200,
                "User profile retrieved successfully"
            ),
        },
    )
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return ApiResponse.success(
            data=serializer.data,
            message="User profile retrieved successfully",
            status_code=status.HTTP_200_OK
        )
