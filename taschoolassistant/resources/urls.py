from django.urls import path
from .views import ResourceView, ResourceViewById

urlpatterns = [
    path("", ResourceView.as_view(), name="resource"),
    path("<int:resource_id>", ResourceViewById.as_view(), name="resource"),
]
