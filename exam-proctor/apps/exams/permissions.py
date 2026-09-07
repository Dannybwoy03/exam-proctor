from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Exam, Question, QuestionBank


def user_can_manage_course(user, course) -> bool:
    if user.is_admin_user:
        return True
    if not user.is_teacher_user:
        return False
    profile = getattr(user, "teacher_profile", None)
    return profile is not None and course.teacher_id == profile.pk


def get_bank_for_user(user, bank_id) -> QuestionBank:
    bank = get_object_or_404(QuestionBank.objects.select_related("course__teacher__user"), pk=bank_id)
    if not user_can_manage_course(user, bank.course):
        raise PermissionDenied
    return bank


def get_exam_for_user(user, exam_id) -> Exam:
    exam = get_object_or_404(Exam.objects.select_related("course__teacher__user"), pk=exam_id)
    if not user_can_manage_course(user, exam.course):
        raise PermissionDenied
    return exam


def get_question_for_user(user, bank_id, question_id) -> Question:
    bank = get_bank_for_user(user, bank_id)
    return get_object_or_404(Question, pk=question_id, question_bank=bank)
