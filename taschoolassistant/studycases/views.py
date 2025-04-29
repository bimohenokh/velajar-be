from rest_framework.views import APIView
from .models import StudyCase, StudyCaseAnswer
from .serializers import StudyCaseSerializer, StudyCaseAnswerSerializer
from rest_framework import status

from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError
from taschoolassistant.core.permisssions import IsStudent, IsTeacher
from taschoolassistant.courses.models import CourseInstructor


class StudyCaseView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
        serializer = self.studycase_serializer(data=data)

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
    parser_classes = [MultiPartParser, FormParser]

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
    

class StudyCaseAnswerView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_answer_serializer = StudyCaseAnswerSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated, IsTeacher]
        elif self.request.method == 'POST':
            permission_classes = [IsAuthenticated, IsStudent]
        else:
            permission_classes = [IsAuthenticated] 
        return [permission() for permission in permission_classes]

    def get(self, request, session_id, case_id):
        user = request.user
        is_evaluated = request.GET.get('is_evaluated', None)

        try:
            studycase_answer_instance = StudyCaseAnswer.objects.get_studycase_answer(user, session_id, case_id, is_evaluated)
        except Exception as e:
            raise str(e)

        if not studycase_answer_instance.exists():
            raise NotFound("Study case answer not found")
        
        serializer = self.studycase_answer_serializer(
            studycase_answer_instance, many=True)

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case Answers succesfully retrieved"
        )
    
    def post(self, request, session_id, case_id):
        session = session_id
        user = request.user
        data = request.data.copy()
        data['study_case'] = case_id
        data['student'] = user.id
        data['is_submitted'] = True

        serializer = self.studycase_answer_serializer(data=data)

        if serializer.is_valid():
            serializer.save()

            #Logic nambah poin TODO
            return ApiResponse.success(
                data=serializer.data,
                message="Study Case answer successfully created",
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError(serializer.errors)


class StudyCaseAnswerViewById(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.studycase_answer_serializer = StudyCaseAnswerSerializer

    def get(self, request, session_id, case_id, answer_id):
        # serializer manipulation for showing question also
        user = request.user
        studycase_answer_instance = StudyCaseAnswer.objects.get_studycase_answer_id(user, session_id, case_id, answer_id)
        if not studycase_answer_instance:
            raise NotFound("Study Case answer not found")

        serializer = self.studycase_answer_serializer(studycase_answer_instance)
        return ApiResponse.success(serializer.data, message="Study Case answer successfully retrieved")

    def patch(self, request, session_id, case_id, answer_id):
        try:
            study_case = StudyCaseAnswer.objects.get(study_case=case_id, id=answer_id)
        except StudyCaseAnswer.DoesNotExist:
            raise NotFound("Study Case not found.")
        
        #pengecekan buat isevaluated

        serializer = self.studycase_answer_serializer(study_case, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Study Case successfully updated",
            status_code=status.HTTP_200_OK
        )