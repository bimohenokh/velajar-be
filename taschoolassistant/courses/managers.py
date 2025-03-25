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
        return self.get(
            courseparticipant__participant=user,
            courseparticipant__is_participating=True,
            id=id
        )


class CourseInstructorManager(Manager):
    pass


class CourseParticipantManager(Manager):
    def read_all(self, user):
        """
        Retrieve all records from the Course Model.
        """
        return self.filter(name=user)


class CourseSessionManager(Manager):
    pass


class CourseSessionResourceManager(Manager):
    pass
