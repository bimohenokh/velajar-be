from django.db.models import Manager


class ChainNoteManager(Manager):
    def get_queryset(self):
        return super().get_queryset()

