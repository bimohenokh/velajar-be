from django.db.models import Manager
from django.db.models import OuterRef, Exists
from taschoolassistant.courses.models import CourseParticipant

class ResourceManager(Manager):
    def get_queryset(self):
        return super().get_queryset()

    # def get_resources(self, user, session_id):
    #     query = self.filter(
    #      course_session__course__courseparticipant__participant=user,  # FIXME ini query user buat apa dah, ntar tanya
    #      course_session__course__courseparticipant__is_participating=True,
    #      course_session=session_id)
    #
    #
    #     return query
        # valid_participant = CourseParticipant.objects.filter(
        #     participant=user.id,
        #     is_participating=True,
        #     course=OuterRef('course_session__course')
        # )

        # return self.filter(
        #         course_session=session_id
        #     ).annotate(
        #         is_valid_participant=Exists(valid_participant)
        #     ).filter(
        #         is_valid_participant=True
        #     )
