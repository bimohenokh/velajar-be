from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone

# quizzes/views.py
from .models import Quiz, Question, QuizAttempt, Answer, Option
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer, QuizAttemptSerializer, OptionSerializer

from taschoolassistant.core.utils.response import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

class QuizView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_serializer = QuizSerializer
        self.option_serializer = OptionSerializer

    # GET ALL QUIZZES BY COURSE SESSION
    def get(self, request):
        try:
            course_session = request.data['course_session']
            quizzes = Quiz.objects.filter(course_session=course_session)
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

        if not request.user.role == "teacher":
            raise ValidationError("You do not have permission to create a quiz")

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
        
        if not request.user.role == "teacher":
            raise ValidationError("You do not have permission to create a quiz")
            
        # Check if request data is empty
        if not request.data:
            raise ValidationError("Request body cannot be empty")
            
        try:
            quiz = Quiz.objects.get(id=quiz_id)

            serializer = self.question_serializer(data=request.data, context={'quiz': quiz})

            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    data=serializer.data,
                    message="Question successfully created",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                raise ValidationError(serializer.errors)
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")

    # GET ALL QUESTIONS BY QUIZ ID
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            questions = Question.objects.filter(quiz=quiz)
            serializer = self.question_serializer(questions, many=True)
            return ApiResponse.success(
                data=serializer.data,
                message="Quiz questions successfully retrieved"
            )
        except KeyError:
            raise ValidationError("Quiz id is required")
        except Quiz.DoesNotExist:
            raise NotFound("Quiz questions not found")
    
    def patch(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")
        
        if not request.user.role == "teacher":
            raise ValidationError("You do not have permission to create a quiz")
            
        # Check if request data is empty
        if not request.data:
            raise ValidationError("Request body cannot be empty")
            
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            question = Question.objects.get(id=request.data['question_id'], quiz=quiz)
            serializer = self.question_serializer(question, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    data=serializer.data,
                    message="Question updated successfully",
                    status_code=status.HTTP_200_OK
                )
            else:
                raise ValidationError(serializer.errors)
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")
    
    def delete(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")
        
        if not request.user.role == "teacher":
            raise ValidationError("You do not have permission to create a quiz")
            
        # Check if request data is empty
        if not request.data:
            raise ValidationError("Request body cannot be empty")
            
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            question = Question.objects.get(id=request.data['question_id'], quiz=quiz)
            question.delete()
            return ApiResponse.success(
                message="Question successfully deleted",
                status_code=status.HTTP_200_OK
            )
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")
        except Question.DoesNotExist:
            raise NotFound("Question not found in this quiz")


class StartQuizView(APIView):
    permission_classes = [IsAuthenticated]

    # START QUIZ BY QUIZ ID
    def post(self, request, quiz_id):
        # Check if quiz_id is provided
        if quiz_id is None:
            raise ValidationError("Quiz id is required in the URL")

        if not request.user.role == "teacher":
            raise ValidationError("You do not have permission to create a quiz")
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.status == 'active':
                raise ValidationError("Quiz has already started")
            if quiz.status == 'finished':
                raise ValidationError("Quiz was already finished")
            
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
            if quiz.status == 'draft':
                raise ValidationError("Quiz has not started yet.")
            if quiz.status == 'finished':
                raise ValidationError("Quiz was already finished")
            
                    
            existing_attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
            if existing_attempt:
                if existing_attempt.is_submitted:
                    raise ValidationError("You have already completed this quiz.")
                else:
                    raise ValidationError("You have already started this quiz.")
                        
            quiz_attempt = QuizAttempt.objects.create(quiz=quiz, student=request.user, started_at=timezone.now())

            return ApiResponse.success(
                data=self.quiz_attempt_serializer(quiz_attempt).data,
                message="Quiz attempt successfully started",
                status_code=status.HTTP_201_CREATED
            )
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found")
        
class AnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answer_serializer = AnswerSerializer

    def get(self, request):
                # Check if request data is empty
        if not request.data:
            raise ValidationError("Request body cannot be empty")
        
        try:
            quiz_attempt = QuizAttempt.objects.get(id=request.data['quiz_attempt'], student=request.user)

            answers = Answer.objects.filter(attempt=quiz_attempt)
            serializer = self.answer_serializer(answers, many=True)
            return ApiResponse.success(
                data=serializer.data,
                message="Answer successfully retrieved",
                status_code=status.HTTP_200_OK
            )
        except QuizAttempt.DoesNotExist:
            raise NotFound("Quiz attempt not found")
        except Answer.DoesNotExist:
            raise NotFound("Answer not found")

    # SAVE ANSWER PER QUESTION
    def post(self, request):
        
        try:
            quiz_attempt = QuizAttempt.objects.get(id=request.data['quiz_attempt'], student=request.user)
            if quiz_attempt.is_submitted:
                raise ValidationError("Quiz attempt is already submitted")
            
            question_id = request.data.get('question')
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
                status_code=status.HTTP_201_CREATED
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
            
            answers = Answer.objects.filter(attempt=quiz_attempt)

            answers_data = []
            for ans in answers:
                answers_data.append({
                    'question': ans.question.id,
                    'selected_options': [opt.id for opt in ans.selected_options.all()]
                })

            data = {
                'quiz': quiz_attempt.quiz.id,
                'student': request.user.id,
                'answers': answers_data
            }

            serializer = self.quiz_attempt_serializer(data=data, instance=quiz_attempt, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return ApiResponse.success(
                data=serializer.data,
                message="Answer successfully submitted",
                status_code=status.HTTP_200_OK
            )
        except QuizAttempt.DoesNotExist:
            raise NotFound("Quiz attempt not found")

