import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from .models import (
    Course,
    CourseParticipant,
    CourseInstructor,
    CourseSession,
    CourseInviteToken,
)
from .schemas import course_schema, course_by_id_schema
from .serializers import (
    CourseSerializer,
    CourseSessionSerializer,
    CreateCourseInviteTokenSerializerIn,
    CourseInviteTokenSerializer,
    CourseParticipantSerializer,
)
from rest_framework import status

from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied


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

    def patch(self, request, pk=None):
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


class CourseSessionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_session_serializer = CourseSessionSerializer

    def get(self, request, course_id):
        user = request.user
        try:
            course_session_instance = CourseSession.objects.get_course_session(user, course_id)
        except Exception as e:
            raise e
        print(course_session_instance)
        if not course_session_instance.exists():
            raise NotFound("Course Sessions not found")
        serializer = self.course_session_serializer(
            course_session_instance, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Course sessions succesfully retrieved"
        )

    def post(self, request, course_id):
        user = request.user
        data = request.data.copy()  
        data['course'] = course_id 

        serializer = self.course_session_serializer(data=data)

        if serializer.is_valid():
            course_session = serializer.save()
            return ApiResponse.success(
                data=serializer.data,
                message="Course session successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError("Invalid input data type")
        

class CourseSessionViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_session_serializer = CourseSessionSerializer

    def get(self, request, course_id, session_id):
        user = request.user
        course_instance = CourseSession.objects.get_detail_course_session_by_id(user, course_id, session_id)
        if not course_instance:
            raise NotFound("Course session not found")

        serializer = self.course_session_serializer(course_instance)
        return ApiResponse.success(serializer.data, message="Course session successfully retrieved")

    def patch(self, request, course_id, session_id):
        print(request.data)
        try:
            course_session = CourseSession.objects.get(course=course_id, pk=session_id)
        except CourseSession.DoesNotExist:
            raise NotFound("Course session not found.")
        
        print(course_session)

        serializer = self.course_session_serializer(course_session, data=request.data, partial=True)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Course session successfully updated",
            status_code=status.HTTP_200_OK
        )

    def delete(self, request, course_id, session_id):
        try:
            course_session = CourseSession.objects.get(pk=session_id, course=course_id)
        except CourseSession.DoesNotExist:
            raise NotFound("Course session not found.")

        course_session.delete()

        return ApiResponse.success(
            message="Course session successfully deleted",
            status_code=status.HTTP_204_NO_CONTENT
        )

class InviteCourseWithLink(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course_instance = Course.objects.get(id=course_id)
        if not course_instance:
            raise NotFound("Course not found")

        # check if user is the course instructor
        try:
            user_instructor = CourseInstructor.objects.get(
                course_participant__course=course_instance, course_participant__participant=request.user
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied(detail="User is not authorized to invite to this course")

        # create a link with a token that can be used to join the course
        valid_request = CreateCourseInviteTokenSerializerIn(data=request.data)
        valid_request.is_valid(raise_exception=True)

        generated_token = uuid.uuid4().hex
        expired_at = timezone.now() + timedelta(hours=1)
        new_course_invite_token = CourseInviteToken.objects.create(
            course=course_instance,
            token=generated_token,
            role=valid_request.validated_data["role"],
            expired_at=expired_at
        )

        out_serializer = CourseInviteTokenSerializer(new_course_invite_token)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Course invitation link successfully sent",
            status_code=status.HTTP_200_OK
        )


class SubmitCourseInviteToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        role = request.query_params.get("role", None)
        if not role:
            raise ValidationError("Role is required")

        try:
            course_invite_token = CourseInviteToken.objects.get(token=request.data["token"], role=role)
        except CourseInviteToken.DoesNotExist:
            raise NotFound("Course invite token not found")

        # check if token is expired
        if course_invite_token.expired_at < timezone.now():
            raise PermissionDenied("Course invite token is expired", code="url_link_expired")

        # check if token role and user role same
        if not course_invite_token.is_user_and_token_role_same(request.user):
            raise PermissionDenied("Course invite token is not valid", code="url_link_invalid")

        # check if user already joined the course
        # if not create course participant
        if course_invite_token.is_for_student:
            try:
                course_participant = CourseParticipant.objects.get(
                    course_id=course_invite_token.course_id,
                    participant_id=request.user.id
                )
                if course_participant.is_participating:
                    pass
                else:
                    course_participant.is_participating = True
                    course_participant.save()
            except CourseParticipant.DoesNotExist:
                course_participant = CourseParticipant.objects.create(
                    course_id=course_invite_token.course_id,
                    participant_id=request.user.id,
                    is_participating=True
                )

        elif course_invite_token.is_for_teacher:
            try:
                course_participant = CourseParticipant.objects.get(
                    course_id=course_invite_token.course_id,
                    participant_id=request.user.id
                )
                if course_participant.is_participating:
                    pass
                else:
                    course_participant.is_participating = True
                    course_participant.save()

            except CourseParticipant.DoesNotExist:
                with transaction.atomic():
                    course_participant = CourseParticipant.objects.create(
                        course_id=course_invite_token.course_id,
                        participant_id=request.user.id,
                        is_participating=True
                    )
                    CourseInstructor.objects.create(
                        course_participant=course_participant,
                        is_owner=False
                    )

        else:
            raise ValidationError("Invalid role")

        out_serializer = CourseParticipantSerializer(course_participant)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Course invite token successfully retrieved",
            status_code=status.HTTP_200_OK
        )