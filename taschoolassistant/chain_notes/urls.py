from django.urls import path

from taschoolassistant.chain_notes.views import (
    ChainNoteView,
    ChainNoteViewById,
    StartChainNoteView,
    CurrentChainNoteTurnView,
    SkipChainNoteTurnView,
)

urlpatterns = [
    path("", ChainNoteView.as_view(), name="chain_note"),
    path("<int:pk>/", ChainNoteViewById.as_view(), name="chain_note_by_id"),
    path("<int:pk>/start/", StartChainNoteView.as_view(), name="chain_note_start"),
    path("<int:pk>/turns/current/", CurrentChainNoteTurnView.as_view(), name="chain_note_current_turn"),
    path("<int:chain_note_pk>/turns/skip", SkipChainNoteTurnView.as_view(), name="chain_note_turn_by_id"),
]

