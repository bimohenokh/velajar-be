from taschoolassistant.studycases.models import StudyCase, StudyCaseStatus


def finish_study_case_name(study_case_id):
    return f"finish_study_case_id_{study_case_id}"


def finish_study_case(study_case_id):
    study_case = StudyCase.objects.get(id=study_case_id)

    if study_case.status == StudyCaseStatus.ACTIVE:
        study_case.status = StudyCaseStatus.FINISHED
        study_case.save()
