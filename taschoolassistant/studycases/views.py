import traceback
from django.utils import timezone
from django_q.tasks import schedule
from rest_framework.generics import get_object_or_404

from rest_framework.views import APIView
from .models import StudyCase, StudyCaseAnswer, StudyCaseStatus, StudyCaseAttempt
from .serializers import (
    StudyCaseWithQuestionsSerializer,
    StudyCaseParamSerializer,
    StudyCaseSerializer,
    StudyCaseAttemptSerializer,
)
from rest_framework import status
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, ValidationError
from taschoolassistant.core.permisssions import IsStudent, IsTeacher
from taschoolassistant.users.serializers import UserSerializer
from taschoolassistant.courses.models import (
    ParticipantPoint,
    CourseSession,
    CourseParticipant,
)
from taschoolassistant.users.models import User
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied

from .tasks import finish_study_case


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

        out_serializer = StudyCaseSerializer(studycase)

        return ApiResponse.success(
            data=out_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        data = request.data
        # TODO check if user is course instructor of the course

        serializer = StudyCaseWithQuestionsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
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

    def patch(self, request, case_id):
        try:
            study_case = StudyCase.objects.get(id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        # TODO check if user is course instructor of the course

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


# FIXME
# class StudyCaseAnswerReadStudentSubmittedView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.studycase_answer_serializer = UserSerializer  # FIXME kenapa jadi user serializer
#
#     def get(self, request, session_id, case_id):
#
#         is_evaluated = request.GET.get('is_evaluated')
#         search = request.GET.get('search')
#         print(is_evaluated)
#
#         answered_students = User.objects.filter(
#             studycaseanswer__study_case_question__study_case_id=case_id,
#             studycaseanswer__is_submitted=True,
#             studycaseanswer__study_case_question__study_case__course_session_id=session_id
#         ).distinct()
#
#         if is_evaluated:
#             answered_students = answered_students.filter(studycaseanswer__is_evaluated=True) if is_evaluated == "Sudah Dievaluasi" else answered_students.filter(studycaseanswer__is_evaluated=False)
#
#         if search:
#             answered_students = answered_students.filter(nama_lengkap__icontains=search)
#
#         if not answered_students.exists():
#             raise NotFound("Student has't submitted yet")
#
#
#         serializer = self.studycase_answer_serializer(answered_students, many=True)
#
#         return ApiResponse.success(
#             data=serializer.data,
#             message="Study Case Answers Submitted successfully retrieved"
#         )








# class StudyCaseAnswerView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def get(self, request, case_id):
#         study_case = get_object_or_404(StudyCase, id=case_id)
#
#         # TODO Check if user is course participant of the course
#
#
#
#
#         return ApiResponse.success(
#             data=serializer.data,
#             message="Study Case Answers successfully retrieved"
#         )
#
#
# class StudyCaseAnswerReadView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.studycase_answer_serializer = StudyCaseAnswerReadSerializers
#
#     def get(self, request, session_id, case_id, student_id):
#         user = request.user
#
#         try:
#             student = User.objects.get(id=student_id)
#         except User.DoesNotExist:
#             raise NotFound("Student not found")
#
#
#         try:
#             answers_qs = StudyCaseAnswer.objects.get_studycase_answer(
#                 requester=user,
#                 session_id=session_id,
#                 case_id=case_id,
#                 target_student=student
#             )
#         except Exception as e:
#             traceback.print_exc()
#             raise APIException(f"Error in manager: {str(e)}")  # FIXME tambahin status
#
#         if not answers_qs.exists():
#             raise NotFound("Study case answer not found")
#
#         serializer = StudyCaseAnswerReadSerializers(answers_qs, many=True)
#
#         return ApiResponse.success(
#             data=serializer.data,
#             message="Study Case Answers successfully retrieved"
#         )
#
#
# class StudyCaseAnswerWriteView(APIView):
#     permission_classes = [IsAuthenticated, IsStudent]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.studycase_answer_serializer = StudyCaseAnswerWriteSerializer
#
#     def post(self, request):
#         user = request.user
#         incoming_data = request.data
#
#         if isinstance(incoming_data, list):
#             for item in incoming_data:
#                 # Check if this answer already exists and is submitted
#                 exists = StudyCaseAnswer.objects.filter(
#                     student=user,
#                     is_submitted=True
#                 ).exists()
#                 if exists:
#                     raise PermissionDenied("You have already submitted an answer for one or more questions.")
#
#                 item['student'] = user.id
#                 item['is_submitted'] = True
#                 item['is_evaluated'] = False
#         else:
#             # Check for single input
#             if StudyCaseAnswer.objects.filter(
#                 student=user,
#                 is_submitted=True
#             ).exists():
#                 raise PermissionDenied("You have already submitted an answer for this question.")
#
#             incoming_data['student'] = user.id
#             incoming_data['is_submitted'] = True
#             incoming_data['is_evaluated'] = False
#
#         many = isinstance(incoming_data, list)
#         serializer = self.studycase_answer_serializer(data=incoming_data, many=many)
#
#         if serializer.is_valid():
#             serializer.save()
#             return ApiResponse.success(
#                 data=serializer.data,
#                 message="Study Case answer(s) successfully created",
#                 status_code=status.HTTP_201_CREATED
#             )
#         else:
#             raise ValidationError(serializer.errors)
#
#
# class StudyCaseAnswerPatchView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.studycase_answer_serializer = StudyCaseAnswerReadSerializers
#
#
#     # per question
#     def patch(self, request, session_id, student_id, question_id):
#         data = request.data.copy()
#
#         try:
#             student = User.objects.get(id=student_id)
#         except User.DoesNotExist:
#             raise NotFound("Student not found")
#         print(student)
#
#         try:
#             study_case = StudyCaseAnswer.objects.get(student=student, study_case_question=question_id)
#         except StudyCaseAnswer.DoesNotExist:
#             raise NotFound("Study Case not found.")
#
#         data['is_evaluated'] = True
#         serializer = StudyCaseAnswerWriteSerializer(study_case, data=data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         try:
#             session = CourseSession.objects.get(id=session_id)
#         except CourseSession.DoesNotExist:
#             raise NotFound("Course session not found.")
#
#         course = session.course
#         print(course)
#         print(student)
#
#         try:
#             participant_point = ParticipantPoint.objects.get(
#                 course_participant__participant=student,
#                 course_participant__course=course
#             )
#         except ParticipantPoint.DoesNotExist:
#             raise NotFound("Participant point not found")
#
#
#         participant_point.point_achieved += float(data['point'])
#         participant_point.save()
#
#         return ApiResponse.success(
#             data=serializer.data,
#             message="Evaluation successfully updated",
#             status_code=status.HTTP_200_OK
#         )


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
        )

        return ApiResponse.success(
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

        # TODO should i stop the scheduller?

        return ApiResponse.success(
            message="Study Case successfully stopped",
            status_code=status.HTTP_200_OK
        )


class StudyCaseAttemptView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, case_id):
        study_case = get_object_or_404(StudyCase, id=case_id)

        # TODO Check if user is course participant of the course

        study_case_attempts = StudyCaseAttempt.objects.filter(
            study_case="study_case",
        )

        out_serializer = StudyCaseAttemptSerializer(study_case_attempts, many=True)

        return ApiResponse.success(
            data=out_serializer.data,
            message="Study Case successfully retrieved"
        )