from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Course
from ..serializers import CourseSerializer


class CourseViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.course1 = Course.objects.create(id=1, name="Course 1")
        self.course2 = Course.objects.create(id=2, name="Course 2")
        self.valid_url = reverse(
            'course-detail', kwargs={'pk': self.course1.pk})
        self.invalid_url = reverse('course-detail', kwargs={'pk': 9999})
        self.valid_list_url = reverse('course')

    @patch('taschoolassistant.courses.models.CourseManager.read_by_id')
    def test_get_single_course_success(self, mock_read_by_id):
        """Test retrieving a single course successfully"""
        mock_read_by_id.return_value = self.course1
        response = self.client.get(self.valid_url)
        expected_data = CourseSerializer(self.course1).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], expected_data)

    @patch('taschoolassistant.courses.models.CourseManager.read_all')
    def test_get_all_courses_success(self, mock_read_all):
        """Test retrieving all courses successfully"""
        mock_read_all.return_value = Course.objects.all()
        response = self.client.get(self.valid_list_url)
        expected_data = CourseSerializer(
            [self.course1, self.course2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], expected_data)

    @patch('taschoolassistant.courses.models.CourseManager.read_all')
    def test_get_all_courses_empty(self, mock_read_all):
        """Test retrieving courses when none exist"""
        mock_read_all.return_value = Course.objects.none()
        response = self.client.get(self.valid_list_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Courses empty")

    @patch('taschoolassistant.courses.models.CourseManager.read_by_id')
    def test_get_course_exception_handling(self, mock_read_by_id):
        """Test handling of unexpected exceptions in GET request"""
        mock_read_by_id.side_effect = Exception("Unexpected error")
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Unexpected error")

    @patch('taschoolassistant.courses.models.CourseManager.read_by_id')
    def test_get_course_id_not_found(self, mock_read_by_id):
        """Test handling of id not found in courses"""
        mock_read_by_id.return_value = None
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "No course found")
