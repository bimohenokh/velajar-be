from django.urls import path
from .views import CourseReadView, CoursePostView, CourseDeleteView, CourseDetailView, CourseUpdateView

urlpatterns = [
    path("", CourseReadView.as_view(), name="course"),
    path("create/", CoursePostView.as_view(), name="create-course"),
    path("detail/<int:pk>", CourseDetailView.as_view(), name="detail-course"),
    path("update/<int:pk>", CourseUpdateView.as_view(), name="update-course"),
    path("delete/<int:pk>", CourseDeleteView.as_view(), name="delete-course"),

]
