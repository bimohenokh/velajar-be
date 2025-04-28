from rest_framework.views import APIView
from rest_framework import status
from datetime import timezone

# quizzes/views.py
from .models import Quiz, Question, QuizAttempt, Answer
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer, QuizAttemptSerializer

from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

class QuizView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_serializer = QuizSerializer

    # GET ALL QUIZZES BY COURSE SESSION
    def get(self, request):
        try:
            course_session = request.data['course_session']
            quizzes = Quiz.objects.get(course_session=course_session)
            serializer = self.quiz_serializer(quizzes, many=True)

            return ApiResponse.success(
                data=serializer.data,
                message="Quizzes successfully retrieved"
            )
        except KeyError:
            raise ValidationError("Course session is required")
        except Quiz.DoesNotExist:
            raise NotFound("Quizzes not found")

    # CREATE NEW QUIZ
    def post(self, request):
        # Check if request data is empty
        if not request.data:
            raise ValidationError("Request body cannot be empty")

        try:
            user = request.user
            serializer = self.quiz_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user)
                return ApiResponse.success(
                    data=serializer.data,
                    message="Quiz successfully created",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                # Handle serializer validation errors
                raise ValidationError(serializer.errors)
        except KeyError:
            raise ValidationError("Invalid input data type")

class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_serializer = QuizSerializer
    
    # GET QUIZ DETAIL BY ID
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            serializer = self.quiz_serializer(quiz)
            return ApiResponse.success(
                data=serializer.data,
                message="Quiz detail successfully retrieved"
            )
        except KeyError:
            raise ValidationError("Quiz id is required")
        except Quiz.DoesNotExist:
            raise NotFound("Quiz detail not found")

class QuestionByQuizIdView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question_serializer = QuestionSerializer
    
    # ADD QUESTION TO QUIZ BY QUIZ ID
    def post(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")
            
        # Check if request data is empty
        if not request.data:
            raise ValidationError("Request body cannot be empty")
            
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            serializer = self.question_serializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(quiz=quiz)
                return ApiResponse.success(
                    data=serializer.data,
                    message="Question successfully created",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                # Handle serializer validation errors
                raise ValidationError(serializer.errors)
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")

    # GET ALL QUESTIONS BY QUIZ ID
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            questions = Question.objects.get(quiz=quiz)
            serializer = self.question_serializer(questions, many=True)
            return ApiResponse.success(
                data=serializer.data,
                message="Quiz questions successfully retrieved"
            )
        except KeyError:
            raise ValidationError("Quiz id is required")
        except Quiz.DoesNotExist:
            raise NotFound("Quiz questions not found")


class StartQuizView(APIView):
    permission_classes = [IsAuthenticated]

    # START QUIZ BY QUIZ ID
    def post(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.status = 'active'
            quiz.started_at = timezone.now()
            quiz.save()

            return ApiResponse.success(
                message="Quiz successfully started",
                status_code=status.HTTP_201_CREATED
            )
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")
        

class StopQuizView(APIView):
    permission_classes = [IsAuthenticated]

    # STOP QUIZ BY QUIZ ID
    def post(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.status = 'finished'
            quiz.save()

            return ApiResponse.success(
                message="Quiz successfully stopped",
                status_code=status.HTTP_201_CREATED
            )
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")
        
class StartAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_attempt_serializer = QuizAttemptSerializer

    # START QUIZ ATTEMPT BY QUIZ ID
    def post(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz_attempt = QuizAttempt.objects.create(quiz=quiz, student=request.user, started_at=timezone.now())

            return ApiResponse.success(
                data=self.quiz_attempt_serializer(quiz_attempt).data,
                message="Quiz attempt successfully started",
                status_code=status.HTTP_201_CREATED
            )
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")
        
class SaveAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answer_serializer = AnswerSerializer

    # SAVE ANSWER PER QUESTION
    def post(self, request):
        
        try:
            quiz_attempt = QuizAttempt.objects.get(id=request.data['quiz_attempt'], student=request.user)
            if quiz_attempt.is_submitted:
                raise ValidationError("Quiz attempt is already submitted")
            
            question_id = request.data.get('question_id')
            selected_options = request.data.get('selected_options', [])
            if not question_id or not selected_options:     
                raise ValidationError("Question and selected options are required")

            question = Question.objects.get(id=question_id, quiz=quiz_attempt.quiz)

            # Update or create answer
            answer, created = Answer.objects.get_or_create(
                attempt=quiz_attempt,
                question=question
            )
            answer.selected_options.set(selected_options)
            answer.save()
            serializer = self.answer_serializer(answer)
            return ApiResponse.success(
                data=serializer.data,
                message="Answer successfully saved",
                status_code=status.HTTP_200_OK
            )
        except QuizAttempt.DoesNotExist:
            raise NotFound("Quiz attempt not found")
        except Question.DoesNotExist:
            raise NotFound("Question not found in this quiz")


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answer_serializer = AnswerSerializer
        self.quiz_attempt_serializer = QuizAttemptSerializer

    # SUBMIT QUIZ ATTEMPT
    def post(self, request):
        
        try:
            quiz_attempt = QuizAttempt.objects.get(id=request.data['quiz_attempt'], student=request.user)
            if quiz_attempt.is_submitted:
                raise ValidationError("Quiz attempt is already submitted")
            data = {}
            data['answers'] = Answer.objects.get(attempt=quiz_attempt)
            data['quiz'] = quiz_attempt.quiz.id

            serializer = self.quiz_attempt_serializer(data=data)
            if serializer.is_valid():
                serializer.save()

            return ApiResponse.success(
                data=serializer.data,
                message="Answer successfully submitted",
                status_code=status.HTTP_200_OK
            )
        except QuizAttempt.DoesNotExist:
            raise NotFound("Quiz attempt not found")
        except Question.DoesNotExist:
            raise NotFound("Question not found in this quiz")

