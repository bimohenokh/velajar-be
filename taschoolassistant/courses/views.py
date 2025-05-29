import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from .models import (
    Course,
    CourseParticipant,
    CourseInstructor,
    CourseSession,
    CourseInviteToken,
    ParticipantPoint,
)
from .schemas import course_schema, course_by_id_schema
from .serializers import (
    CourseSerializer,
    CourseSessionSerializer,
    CreateCourseInviteTokenSerializerIn,
    CourseInviteTokenSerializer,
    CourseParticipantSerializer,
    LeaderboardSerializer, CourseSessionFeatureSerializer,
)
from rest_framework import status

from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from ..chain_notes.models import ChainNote
from ..quiz.models import Quiz
from ..resources.models import Resource
from ..studycases.models import StudyCase


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
        courses_instance = Course.objects.get_courses(user, name, jenjang)
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
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            course = serializer.save()

            course_participant = CourseParticipant.objects.create(
                course=course,
                participant=user,
                is_participating=True,
            )

            course_instructor = CourseInstructor.objects.create(
                course_participant=course_participant,
                is_owner=True
            )

        return ApiResponse.success(
            data=serializer.data,
            message="Course successfully created",
            status_code=status.HTTP_201_CREATED
        )


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_session_serializer = CourseSessionSerializer

    def get(self, request, course_id):
        user = request.user

        course_session_instance = CourseSession.objects.get_course_session(user, course_id)

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

        try:
            course_session = CourseSession.objects.get(course=course_id, pk=session_id)
        except CourseSession.DoesNotExist:
            raise NotFound("Course session not found.")
        


        serializer = self.course_session_serializer(course_session, data=request.data, partial=True)
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


class CourseSessionFeatureViewById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):

        course_session = get_object_or_404(CourseSession, pk=session_id)

        # TODO check if user is participant of the course

        try:
            chan_note = ChainNote.objects.get(course_session=course_session)
            chain_note_id = chan_note.id
        except ChainNote.DoesNotExist:
            chain_note_id = None

        try:
            study_cases = StudyCase.objects.get(course_session=course_session)
            study_case_id = study_cases.id
        except StudyCase.DoesNotExist:
            study_case_id = None

        try:
            quiz = Quiz.objects.get(course_session=course_session)
            quiz_id = quiz.id
        except Quiz.DoesNotExist:
            quiz_id = None

        resources = list(Resource.objects.filter(course_session=course_session))
        if len(resources) != 0:
            resource_ids = True
        else:
            resource_ids = False

        out_serializer = CourseSessionFeatureSerializer(
            {
                "chain_note_id": chain_note_id,
                "study_case_id": study_case_id,
                "quiz_id": quiz_id,
                "resource_ids": resource_ids
            }
        )

        return ApiResponse.success(out_serializer.data, message="Course session features successfully retrieved")


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_session_serializer = LeaderboardSerializer

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise NotFound("Course not found.")

        # Filter points by course
        participant_points = ParticipantPoint.objects.filter(course_participant__course=course).order_by('-point_achieved')
        serializer = self.course_session_serializer(participant_points, many=True)

        return ApiResponse.success(serializer.data, message="Leaderboard successfully retrieved")


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

    def post(self, request, token_str):

        # FIXME perlu param gk ya
        # role = request.query_params.get("role", None)
        # if not role:
        #     raise ValidationError("Role is required")

        try:
            course_invite_token = CourseInviteToken.objects.get(token=token_str)
        except CourseInviteToken.DoesNotExist:
            raise NotFound("Course invite token not found")

        # check if token is expired
        if course_invite_token.expired_at < timezone.now():
            raise PermissionDenied("Course invite token is expired", code="url_link_expired")

        # check if token role and user role same
        if not course_invite_token.is_user_and_token_role_same(request.user):
            raise PermissionDenied("Your role is different with the token", code="role_mismatch")

        # check if user already joined the course
        # if not create course participant
        with transaction.atomic():
            if course_invite_token.is_for_student:
                try:
                    course_participant = CourseParticipant.objects.get(
                        course_id=course_invite_token.course_id,
                        participant_id=request.user.id
                    )
                    if course_participant.is_participating:
                        # If the user is already participating, do nothing
                        pass
                    else:
                        course_participant.is_participating = True
                        course_participant.save()
                except CourseParticipant.DoesNotExist:
                    course_participant = CourseParticipant.objects.create(
                        course_id=course_invite_token.course_id,
                        participant_id=request.user.id,
                        is_participating=True,
                    )
                    participant_point = ParticipantPoint.objects.create(
                        course_participant=course_participant, point_achieved=0
                    )

            elif course_invite_token.is_for_teacher:
                try:
                    course_participant = CourseParticipant.objects.get(
                        course_id=course_invite_token.course_id,
                        participant_id=request.user.id
                    )
                    if course_participant.is_participating:
                        # If the user is already participating, do nothing
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
                    CourseInstructor.objects.create(
                        course_participant=course_participant,
                        is_owner=False
                    )

            else:
                raise ValidationError("Invalid role")

        out_serializer = CourseParticipantSerializer(course_participant)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Successfully joined the course",
            status_code=status.HTTP_200_OK
        )