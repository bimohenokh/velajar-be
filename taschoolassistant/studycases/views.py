from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import schedule
from rest_framework.generics import get_object_or_404

from rest_framework.views import APIView
from .models import StudyCase, StudyCaseAnswer, StudyCaseStatus, StudyCaseAttempt
from .serializers import (
    StudyCaseWithQuestionsSerializer,
    StudyCaseParamSerializer,
    StudyCaseAttemptSerializer,
    StudyCaseAttemptWithAnswersSerializer,
    StudyCaseSerializer,
    StudyCaseAnswerSerializer,
    EvaluateStudyCaseAnswerInSerializer,
)
from rest_framework import status
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, ValidationError
from taschoolassistant.core.permisssions import IsTeacher
from taschoolassistant.courses.models import (
    CourseParticipant,
    ParticipantPoint,
)
from rest_framework.exceptions import PermissionDenied

from .tasks import finish_study_case, finish_study_case_name


class StudyCaseView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        param_serializer = StudyCaseParamSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)

        course_session_id = param_serializer.data['course_session_id']

        # TODO check if user is course participant of the course

        try:
            studycase = StudyCase.objects.get(course_session_id=course_session_id)
        except StudyCase.DoesNotExist:
            raise NotFound("StudyCase not found")

        out_serializer = StudyCaseWithQuestionsSerializer(studycase)

        return ApiResponse.success(
            data=out_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):

        # TODO check if user is course instructor of the course

        serializer = StudyCaseWithQuestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            # data=out_data,
            data=serializer.data,
            message="Study Case successfully created",
            status_code=status.HTTP_201_CREATED
        )


class StudyCaseViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, case_id):
        try:
            study_case = StudyCase.objects.get(id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        # TODO check if user is course participant of the course

        serializer = StudyCaseWithQuestionsSerializer(study_case)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case successfully retrieved",
            status_code=status.HTTP_200_OK
        )

    def put(self, request, case_id):
        try:
            study_case = StudyCase.objects.get(id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        # TODO check if user is course instructor of the course
        if study_case.status != StudyCaseStatus.DRAF:
            raise ValidationError("Study Case is not in draft mode, cannot be updated.")

        serializer = StudyCaseWithQuestionsSerializer(study_case, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case successfully updated",
            status_code=status.HTTP_200_OK
        )

    def delete(self, request, case_id):
        try:
            study_case = StudyCase.objects.get(id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        # TODO check if user is course instructor of the course

        study_case.delete()

        return ApiResponse.success(
            message="Study Case successfully deleted",
            status_code=status.HTTP_204_NO_CONTENT
        )


class StartStudyCaseView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request, case_id):
        try:
            study_case = StudyCase.objects.get(id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        # check if user is allowed
        try:
            course_participant = CourseParticipant.objects.get(
                course_id=study_case.course_session.course_id,
                participant=request.user.id,
            )
            if not course_participant.is_teacher:
                raise PermissionDenied("You do not have permission to start this study case.")
        except:
            raise PermissionDenied("You do not have permission to start this study case.")

        if study_case.status == StudyCaseStatus.ACTIVE:
            raise ValidationError("Quiz has already started")
        if study_case.status == StudyCaseStatus.FINISHED:
            raise ValidationError("Quiz was already finished")

        study_case.status = StudyCaseStatus.ACTIVE
        study_case.started_at = timezone.now()
        study_case.save()

        schedule(
            f'{finish_study_case.__module__}.{finish_study_case.__name__}',
            case_id,
            next_run=study_case.started_at + study_case.time_range,
            schedule_type='O',
            name=finish_study_case_name(study_case.id),
        )

        serializer = StudyCaseSerializer(study_case)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case successfully started",
            status_code=status.HTTP_200_OK
        )


class StopStudyCaseView(APIView):
    def post(self, request, case_id):

        study_case = get_object_or_404(StudyCase, id=case_id)

        # TODO check if user is course instructor of the course

        if study_case.status == StudyCaseStatus.DRAF:
            raise ValidationError("Study Case is still in draft mode")
        if study_case.status == StudyCaseStatus.FINISHED:
            raise ValidationError("Study Case has already finished")

        study_case.status = StudyCaseStatus.FINISHED
        study_case.save()

        # stop the scheduller
        Schedule.objects.get(name=finish_study_case_name(case_id)).delete()

        out_serializer = StudyCaseSerializer(study_case)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Study Case successfully stopped",
            status_code=status.HTTP_200_OK
        )


class StudyCaseAttemptView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, case_id):
        study_case = get_object_or_404(StudyCase, id=case_id)

        # TODO Check if user is course participant of the course

        study_case_attempts = list(StudyCaseAttempt.objects.filter(
            study_case=study_case,
        ).select_related("student__participant"))

        out_serializer = StudyCaseAttemptSerializer(study_case_attempts, many=True)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Study Case successfully retrieved"
        )

    def post(self, request, case_id):
        user = request.user
        study_case = get_object_or_404(StudyCase, id=case_id)

        try:
            # only student can create study case attempt
            course_student = CourseParticipant.objects.get(
                participant=user.id, course_id=study_case.course_session.course_id,
                courseinstructor__isnull=True
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("You are not a student of this course.")

        if study_case.status == StudyCaseStatus.FINISHED:
            raise ValidationError("Study Case has already finished.")

        if study_case.status == StudyCaseStatus.DRAF:
            raise ValidationError("Study Case has not started.")

        serializer = StudyCaseAttemptWithAnswersSerializer(
            data=request.data,
            context={
                'study_case': study_case,
                'student': course_student,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case Attempt successfully created",
            status_code=status.HTTP_201_CREATED
        )


class StudyCaseAttemptByIdView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, attempt_id):
        study_case_attempt = get_object_or_404(StudyCaseAttempt, id=attempt_id)

        # TODO Check if user is course participant of the course

        serializer = StudyCaseAttemptWithAnswersSerializer(study_case_attempt)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case Attempt successfully retrieved",
            status_code=status.HTTP_200_OK,
        )

    # FIXME buat apa ada update kan gk boleh di ubah
    def put(self, request, attempt_id):
        study_case_attempt = get_object_or_404(StudyCaseAttempt.objects.select_related("study_case"), id=attempt_id)

        # TODO Check if user is course participant of the course

        study_case = study_case_attempt.study_case
        if study_case.status != StudyCaseStatus.DRAF:
            raise ValidationError("Study Case is not in draft mode, cannot be updated.")
        if study_case.status == StudyCaseStatus.FINISHED:
            raise ValidationError("Study Case has already finished.")
        if study_case_attempt.is_evaluated:
            raise ValidationError("Study Case Attempt has already been evaluated.")

        serializer = StudyCaseAttemptWithAnswersSerializer(
            study_case_attempt, data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case Attempt successfully updated",
            status_code=status.HTTP_200_OK
        )


class EvaluateStudyCaseAnswerView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def put(self, request, attempt_id):

        study_case_attempt: StudyCaseAttempt = get_object_or_404(
            StudyCaseAttempt.objects.select_related("study_case", "student"), id=attempt_id
        )

        study_case = study_case_attempt.study_case
        if study_case.status != StudyCaseStatus.FINISHED:
            raise ValidationError("Study Case hasn't finished.")

        if study_case_attempt.is_evaluated:
            raise ValidationError("Study Case Attempt has already been evaluated.")

        # TODO Check if user is course instructor of the course

        in_serializer = EvaluateStudyCaseAnswerInSerializer(data=request.data, context={"attempt": study_case_attempt}, many=True)
        in_serializer.is_valid(raise_exception=True)

        with transaction.atomic():

            input_map = {
                item["id"]: item["point"]
                for item in in_serializer.data
                if "id" in item and "point" in item
            }

            available_answers = list(study_case_attempt.answers.all())
            available_ids = {a.id for a in available_answers}
            submitted_ids = set(input_map.keys())

            # Validate all submitted IDs are valid
            invalid_ids = submitted_ids - available_ids
            if invalid_ids:
                raise ValidationError(
                    f"One or more answers are invalid or do not belong to this attempt: {list(invalid_ids)}",
                    code="invalid_answer_ids",
                )

            # Update each answer's point
            for answer in available_answers:
                if answer.id in input_map:
                    answer.point = input_map[answer.id]

            StudyCaseAnswer.objects.bulk_update(available_answers, ["point"])

            # study_case_attempt is evaluated
            study_case_attempt.is_evaluated = True
            study_case_attempt.save()

            # Calculate total points awarded
            total_points = sum(answer.point for answer in available_answers if answer.id in input_map)
            ParticipantPoint.objects.filter(course_participant_id=study_case_attempt.student_id).update(
                point_achieved=F('point_achieved') + total_points
            )

            out_serializer = StudyCaseAnswerSerializer(available_answers, many=True)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Study Case Attempt successfully evaluated",
            status_code=status.HTTP_200_OK
        )




