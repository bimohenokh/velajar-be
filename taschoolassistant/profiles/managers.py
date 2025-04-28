from django.db.models import Manager

class TeacherProfileManager(Manager):

    def get_profile(self, user):
        return self.filter(user=user).first()
         
    
class StudentProfileManager(Manager):

    def get_profile(self, user):
        return self.filter(user=user).first()
