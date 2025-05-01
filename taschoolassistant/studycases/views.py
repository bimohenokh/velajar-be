import traceback
from rest_framework.views import APIView
from .models import StudyCase, StudyCaseAnswer
from .serializers import StudyCaseSerializer, StudyCaseAnswerReadSerializers, StudyCaseAnswerWriteSerializer
from rest_framework import status
from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound, ValidationError
from taschoolassistant.core.permisssions import IsStudent, IsTeacher
from taschoolassistant.users.serializers import UserSerializer
from taschoolassistant.courses.models import ParticipantPoint, CourseSession
from taschoolassistant.users.models import User
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied

class StudyCaseView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_serializer = StudyCaseSerializer

    def get(self, request, session_id):
        user = request.user
        status = request.GET.get('status', None)

        try:
            studycase_instance = StudyCase.objects.get_studycases(user, session_id, status)
        except Exception as e:
            raise str(e)


        if not studycase_instance.exists():
            raise NotFound("Study Cases not found")
        serializer = self.studycase_serializer(
            studycase_instance, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Cases succesfully retrieved"
        )
    
    def post(self, request, session_id):
        user = request.user
        data = request.data.copy()  
        data['course_session'] = session_id 

        serializer = StudyCaseSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse.success(
                data=serializer.data,
                message="Study Case successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError("Invalid input data type")
        

class StudyCaseViewById(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_serializer = StudyCaseSerializer

    def get(self, request, session_id, case_id):
        user = request.user
        studycase_instance = StudyCase.objects.get_studycases_id(user, session_id, case_id)
        if not studycase_instance:
            raise NotFound("Study Case not found")

        serializer = self.studycase_serializer(studycase_instance)
        return ApiResponse.success(serializer.data, message="Study Case successfully retrieved")

    def patch(self, request, session_id, case_id):
        try:
            study_case = StudyCase.objects.get(course_session=session_id, id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        serializer = self.studycase_serializer(study_case, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case successfully updated",
            status_code=status.HTTP_200_OK
        )

    def delete(self, request, session_id, case_id):
        try:
            study_case = StudyCase.objects.get(course_session=session_id, id=case_id)
        except StudyCase.DoesNotExist:
            raise NotFound("Study Case not found.")

        study_case.delete()

        return ApiResponse.success(
            message="Study Case successfully deleted",
            status_code=status.HTTP_204_NO_CONTENT
        )

class StudyCaseAnswerReadStudentSubmittedView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_answer_serializer = UserSerializer

    def get(self, request, case_id):

        answered_students = User.objects.filter(
            studycaseanswer__study_case_question__study_case=case_id,
            studycaseanswer__is_submitted=True,
            studycaseanswer__is_evaluated=False

        ).distinct()
    
        serializer = self.studycase_answer_serializer(answered_students, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case Answers successfully retrieved"
        )

class StudyCaseAnswerReadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_answer_serializer = StudyCaseAnswerReadSerializers

    def get(self, request, session_id, case_id, check_id):
        user = request.user

        try:
            student = User.objects.get(id=check_id)
        except User.DoesNotExist:
            raise NotFound("Student not found")

        is_evaluated = request.GET.get('is_evaluated')
        if is_evaluated is not None:
            is_evaluated = is_evaluated.lower() == 'true'
        

        try:
            answers_qs = StudyCaseAnswer.objects.get_studycase_answer(
                requester=user,
                session_id=session_id,
                case_id=case_id,
                target_student=student,
                is_evaluated=is_evaluated
            )
        except Exception as e:
            traceback.print_exc()
            raise APIException(f"Error in manager: {str(e)}")

        if not answers_qs.exists():
            raise NotFound("Study case answer not found")

        serializer = StudyCaseAnswerReadSerializers(answers_qs, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case Answers successfully retrieved"
        )



class StudyCaseAnswerWriteView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_answer_serializer = StudyCaseAnswerWriteSerializer

    def post(self, request):
        user = request.user
        incoming_data = request.data

        if isinstance(incoming_data, list):
            for item in incoming_data:
                # Check if this answer already exists and is submitted
                exists = StudyCaseAnswer.objects.filter(
                    student=user,
                    is_submitted=True
                ).exists()
                if exists:
                    raise PermissionDenied("You have already submitted an answer for one or more questions.")

                item['student'] = user.id
                item['is_submitted'] = True
                item['is_evaluated'] = False
        else:
            # Check for single input
            if StudyCaseAnswer.objects.filter(
                student=user,
                is_submitted=True
            ).exists():
                raise PermissionDenied("You have already submitted an answer for this question.")

            incoming_data['student'] = user.id
            incoming_data['is_submitted'] = True
            incoming_data['is_evaluated'] = False

        many = isinstance(incoming_data, list)
        serializer = self.studycase_answer_serializer(data=incoming_data, many=many)

        if serializer.is_valid():
            serializer.save()
            return ApiResponse.success(
                data=serializer.data,
                message="Study Case answer(s) successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError(serializer.errors)



class StudyCaseAnswerPatchView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_answer_serializer = StudyCaseAnswerReadSerializers


    def patch(self, request, session_id, check_id, question_id):
        data = request.data.copy()  

        try:
            student = User.objects.get(id=check_id)
        except User.DoesNotExist:
            raise NotFound("Student not found")

        try:
            study_case = StudyCaseAnswer.objects.get(student=student, study_case_question=question_id)
        except StudyCaseAnswer.DoesNotExist:
            raise NotFound("Study Case not found.")
 
        data['is_evaluated'] = True 
        serializer = StudyCaseAnswerWriteSerializer(study_case, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        session = CourseSession.objects.get(id=session_id)
        course = session.course
       
        try:
            participant_point = ParticipantPoint.objects.get(
                course_participant__participant=student, 
                course_participant__course=course
            )
        except ParticipantPoint.DoesNotExist:
            raise NotFound("Participant point not found")
        
        
        participant_point.point_achieved += float(data['point'])
        participant_point.save()
    
        return ApiResponse.success(
            data=serializer.data,
            message="Study Case successfully updated",
            status_code=status.HTTP_200_OK
        )