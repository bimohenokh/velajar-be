from asgiref.sync import sync_to_async
from django.db.models import Manager


class CourseManager(Manager):

    def get_courses(self, user, name, jenjang_kelas):
        query = self.filter(courseparticipant__participant=user,
                            courseparticipant__is_participating=True)

        if name:
            query = query.filter(name__icontains=name)

        if jenjang_kelas:
            query = query.filter(jenjang_kelas=jenjang_kelas)

        return query

    def get_detail_course_by_id(self, user, id):
        return self.filter(
            courseparticipant__participant=user,
            courseparticipant__is_participating=True,
            id=id
        ).first()


class CourseInstructorManager(Manager):
    pass


class CourseParticipantManager(Manager):
    def get_queryset(self):
        return super().get_queryset()

    def read_all(self, user):
        """
        Retrieve all records from the Course Model.
        """
        return self.filter(name=user)

    def get_by_course_id_and_user_id(self, course_id, user_id):
        return self.get(course_id=course_id, user_id=user_id)

    async def aget_by_course_id_and_user_id(self, course_id, user_id):
        return self.aget(course_id=course_id, user_id=user_id)

    def get_by_course_id_and_user_teacher_id(self, course_id, user_teacher_id):
        return (
            self.filter(course_id=course_id)
            .filter(participant_id=user_teacher_id)
            .filter(
                courseinstructor__isnull=False,
            )
            .get()
        )

    async def aget_by_course_id_and_user_teacher_id(self, course_id, user_teacher_id):
        return sync_to_async(self.get_by_course_id_and_user_teacher_id)(course_id, user_teacher_id)

class CourseSessionManager(Manager):
    def get_course_session(self, user, course_id):
        query = self.filter(
            course__courseparticipant__participant=user,
            course__courseparticipant__is_participating=True,
            course__id=course_id
        )
        return query
    
    def get_detail_course_session_by_id(self, user, course_id, session_id):
        return self.filter(
            course__courseparticipant__participant=user,
            course__courseparticipant__is_participating=True,
            course__id=course_id,
            id=session_id
        ).first()


class CourseSessionResourceManager(Manager):
    pass


class CourseInviteTokenManager(Manager):
    def get_queryset(self):
        return super().get_queryset()