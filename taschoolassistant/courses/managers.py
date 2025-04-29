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
    def check_instsructor_for_studycase(self, user, course_session):
        query = self.filter(
            course_participant__participant=user,
            course_participant__course=course_session.course,
            course_participant__is_participating=True
        )
        return 


class CourseParticipantManager(Manager):
    def read_all(self, user):
        """
        Retrieve all records from the Course Model.
        """
        return self.filter(name=user)


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
