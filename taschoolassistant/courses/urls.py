from django.conf import settings
from django.urls import path
from .views import CourseReadView, CoursePostView, CourseDeleteView, CourseDetailView, CourseUpdateView
from django.conf.urls.static import static

urlpatterns = [
    path("", CourseReadView.as_view(), name="course"),
    path("create/", CoursePostView.as_view(), name="create-course"),
    path("detail/<int:pk>", CourseDetailView.as_view(), name="detail-course"),
    path("update/<int:pk>", CourseUpdateView.as_view(), name="update-course"),
    path("delete/<int:pk>", CourseDeleteView.as_view(), name="delete-course"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
