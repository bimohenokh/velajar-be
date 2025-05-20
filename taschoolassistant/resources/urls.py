from django.urls import path
from .views import ResourceView, ResourceViewById

urlpatterns = [
    # path("session/<int:session_id>/", ResourceView.as_view(), name="resource"),
    # path("session/<int:session_id>/resource/<int:resource_id>/", ResourceViewById.as_view(), name="resource-id")
    path("", ResourceView.as_view(), name="resource"),
    path("<int:resource_id>", ResourceView.as_view(), name="resource"),
]
