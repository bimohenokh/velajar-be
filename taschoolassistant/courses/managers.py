from django.db.models import Manager


class CourseManager(Manager):

    def read_all(self):
        """
        Retrieve all records from the Course Model.
        """
        return self.all()

    def read_by_id(self, course_id):
        """
        Retrieve course by id from the Course Model.
        """
        return self.filter(id=course_id).first()


class CourseInstructorManager(Manager):
    pass


class CourseParticipantManager(Manager):
    pass


class CourseSessionManager(Manager):
    pass


class CourseSessionResourceManager(Manager):
    pass
