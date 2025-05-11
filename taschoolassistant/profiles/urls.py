from django.urls import path
from .views import ProfileView, ProfilePostView

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path("<int:user_id>", ProfilePostView.as_view(), name="profile-post" )
]
