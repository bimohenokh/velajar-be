from django.urls import path
from .views import ChainNoteView, ChainNoteViewById

urlpatterns = [
    path("", ChainNoteView.as_view(), name="chain-notes"),
    path("<int:pk>/", ChainNoteViewById.as_view(), name="chain-notes-by-id"),
    # path("<int:pk>/status/", ChainNoteViewById.as_view(), name="chain-notes-by-id")
]

