from django.contrib import admin

from .models import (
    Answer,
    Exam,
    ExamAccessCode,
    ExamAttempt,
    ExamCodeRedemption,
    ExamQuestion,
    ManualGrade,
    Question,
    QuestionBank,
    Result,
)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    inlines = [QuestionInline]


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_published", "duration_minutes")
    list_filter = ("is_published",)
    inlines = [ExamQuestionInline]


@admin.register(ExamAccessCode)
class ExamAccessCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "exam", "is_active", "use_count", "max_uses")


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "status", "attempt_number", "score")
    list_filter = ("status", "grading_status")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "review_status", "marks_awarded")


@admin.register(ManualGrade)
class ManualGradeAdmin(admin.ModelAdmin):
    list_display = ("answer", "graded_by", "marks_awarded", "graded_at")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("attempt", "total_score", "max_score", "finalized_at")
