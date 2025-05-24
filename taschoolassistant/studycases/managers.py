from django.db.models import Manager


class StudyCaseManager(Manager):
   def get_queryset(self):
        return super().get_queryset().prefetch_related('questions')

   # FIXME ntar apus
   # def get_studycases(self, user, session_id, status):
   #    query = self.filter(
   #       course_session__course__courseparticipant__participant=user,
   #       course_session__course__courseparticipant__is_participating=True,
   #       course_session=session_id
   #    )
   #
   #    if status:
   #       query = query.filter(status=status)
   #
   #    return query
   
   def get_studycases_id(self, user, session_id, case_id):
      query = self.filter(
         course_session__course__courseparticipant__participant=user,
         course_session__course__courseparticipant__is_participating=True,
         course_session=session_id,
         id=case_id  # FIXME: ada id tapi ada filter lain?
      ).first()
      return query
   

class StudyCaseQuestionManager(Manager):
   pass


class StudyCaseAttemptManager(Manager):
   def get_queryset(self):
        return super().get_queryset()


class StudyCaseAnswerManager(Manager):

   def get_studycase_answer(self, requester, session_id, case_id, target_student):
      query = self.filter(
         study_case_question__study_case__course_session__course__courseparticipant__participant=requester,
         study_case_question__study_case__course_session__course__courseparticipant__is_participating=True,
         study_case_question__study_case__course_session__id=session_id,
         study_case_question__study_case__id=case_id,
         is_submitted=True,
         student=target_student,
      )

      return query
   
   
   def get_studycase_answer_id(self, user, session_id, case_id, answer_id):
      query = self.filter(
         study_case__course_session__course__courseparticipant__participant=user,
         study_case__course_session__course__courseparticipant__is_participating=True,
         study_case__course_session=session_id,
         study_case=case_id,
         is_submitted=True,
         id= answer_id
      ).first()
      return query