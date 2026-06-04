from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Max
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from pathlib import Path

from django.conf import settings

from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.accounts.portal import render_portal

from .forms import (
    AccessCodeForm,
    AdminAddTimeForm,
    AdminFreezeForm,
    ExamForm,
    ExamQuestionAddForm,
    ManualGradeForm,
    QuestionBankForm,
    QuestionCSVImportForm,
    QuestionForm,
    RedeemCodeForm,
)
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
    get_resumable_attempt,
    grade_attempt,
)
from .permissions import get_bank_for_user, get_exam_for_user, get_question_for_user
from .services.exam_control import add_exam_time, freeze_exam, unfreeze_exam
from .services.question_import import import_questions_from_csv


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def exam_list(request):
    if request.user.is_admin_user:
        exams = Exam.objects.select_related("course").all()
    else:
        exams = Exam.objects.filter(course__teacher__user=request.user).select_related("course")
    return render_portal(
        request,
        "partials/portal/exam_list.html",
        {"exams": exams, "portal_nav": "exams"},
        page_title="Exams",
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def exam_create(request):
    initial = {}
    # Pre-select a course when arriving via "+ Create Exam" on a course row.
    course_id = request.GET.get("course")
    if course_id and course_id.isdigit():
        initial["course"] = int(course_id)
    form = ExamForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        exam = form.save(commit=False)
        exam.created_by = request.user
        exam.save()
        messages.success(request, "Exam created. Add questions from your question banks.")
        return redirect("exams:exam_questions", pk=exam.pk)
    return render(request, "exams/exam_form.html", {"form": form, "title": "Create Exam", "portal_nav": "exams"})


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def exam_detail(request, pk):
    exam = get_exam_for_user(request.user, pk)
    access_codes = exam.access_codes.all()
    exam_questions = exam.exam_questions.select_related("question").order_by("order")
    return render(
        request,
        "exams/exam_detail.html",
        {
            "exam": exam,
            "access_codes": access_codes,
            "exam_questions": exam_questions,
            "portal_nav": "exams",
        },
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def exam_edit(request, pk):
    exam = get_exam_for_user(request.user, pk)
    # Once approved or pending, edits invalidate the approval -- send back to DRAFT.
    locked_state = exam.approval_status in (
        Exam.ApprovalStatus.PENDING,
        Exam.ApprovalStatus.APPROVED,
    )
    form = ExamForm(request.POST or None, instance=exam, user=request.user)
    if request.method == "POST" and form.is_valid():
        edited = form.save(commit=False)
        if locked_state:
            edited.approval_status = Exam.ApprovalStatus.DRAFT
            edited.is_published = False
            edited.submitted_for_approval_at = None
            edited.approved_by = None
            edited.approved_at = None
            edited.rejection_reason = ""
        edited.save()
        if locked_state:
            messages.warning(
                request,
                "Exam was approved/pending. Edits reset it to draft — resubmit for approval.",
            )
        else:
            messages.success(request, "Exam schedule and settings updated.")
        return redirect("exams:detail", pk=exam.pk)
    return render(
        request,
        "exams/exam_form.html",
        {
            "form": form,
            "title": f"Edit — {exam.title}",
            "portal_nav": "exams",
            "exam": exam,
            "locked_state": locked_state,
        },
    )


@require_POST
@role_required(User.Role.TEACHER)
def exam_publish(request, pk):
    # Publishing is the teacher's call after admin approval. Admins approve
    # via admin_exam_review and intentionally don't publish on a teacher's
    # behalf — keeps responsibility unambiguous.
    exam = get_exam_for_user(request.user, pk)
    if exam.approval_status != Exam.ApprovalStatus.APPROVED:
        messages.error(request, "Exam must be approved by an administrator before publishing.")
        return redirect("exams:detail", pk=pk)
    if not exam.exam_questions.exists():
        messages.error(request, "Add at least one question before publishing.")
        return redirect("exams:exam_questions", pk=pk)
    # Re-validate the schedule at publish time: both bounds set, end in the future,
    # and start strictly before end. Approval can happen days before publish.
    now = timezone.now()
    if not exam.available_from or not exam.available_until:
        messages.error(request, "Set both start and end times before publishing.")
        return redirect("exams:detail", pk=pk)
    if exam.available_until <= now:
        messages.error(request, "The exam window has already ended. Update the schedule first.")
        return redirect("exams:edit", pk=pk)
    if exam.available_from >= exam.available_until:
        messages.error(request, "End time must be after start time.")
        return redirect("exams:edit", pk=pk)
    exam.is_published = True
    exam.save(update_fields=["is_published"])
    messages.success(request, "Exam published.")
    return redirect("exams:detail", pk=pk)


@require_POST
@role_required(User.Role.TEACHER)
def exam_submit_for_approval(request, pk):
    # Admins are explicitly excluded — they approve, they don't submit. The
    # exam_detail template hides the button for admins; this is the matching
    # server-side gate so a URL-typed POST still 403s.
    exam = get_exam_for_user(request.user, pk)
    if not exam.exam_questions.exists():
        messages.error(request, "Add questions to the exam before submitting for approval.")
        return redirect("exams:exam_questions", pk=pk)
    if not exam.available_from or not exam.available_until:
        messages.error(request, "Set exam start and end times before submitting for approval.")
        return redirect("exams:detail", pk=pk)
    exam.approval_status = Exam.ApprovalStatus.PENDING
    exam.submitted_for_approval_at = timezone.now()
    exam.rejection_reason = ""
    exam.save(update_fields=["approval_status", "submitted_for_approval_at", "rejection_reason"])
    messages.success(request, "Exam submitted for admin approval.")
    return redirect("exams:detail", pk=pk)


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def generate_access_code(request, pk):
    exam = get_exam_for_user(request.user, pk)
    form = AccessCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.save(commit=False)
        code.exam = exam
        code.created_by = request.user
        code.save()
        messages.success(request, f"Access code created: {code.code}")
        return redirect("exams:detail", pk=pk)
    return render(request, "exams/access_code_form.html", {"form": form, "exam": exam})


@role_required(User.Role.STUDENT)
def redeem_code(request):
    form = RedeemCodeForm(request.POST or None)
    already_redeemed = False
    redeemed_exam = None

    if request.method == "POST" and form.is_valid():
        code_str = form.cleaned_data["code"].strip().upper()
        access_code = ExamAccessCode.objects.filter(code__iexact=code_str).first()
        if access_code is None:
            form.add_error("code", "We couldn't find an access code matching that value.")
        else:
            existing = (
                ExamCodeRedemption.objects.filter(
                    access_code=access_code, student=request.user
                )
                .select_related("access_code__exam")
                .first()
            )
            if existing:
                # Stay on this page with the form disabled — don't redirect and
                # don't use messages.info (that stacks if the student retries).
                already_redeemed = True
                redeemed_exam = existing.access_code.exam
            else:
                # Atomically re-fetch with lock, re-validate, then mint the redemption.
                with transaction.atomic():
                    locked = (
                        ExamAccessCode.objects.select_for_update()
                        .select_related("exam")
                        .get(pk=access_code.pk)
                    )
                    if not locked.is_valid():
                        form.add_error(
                            "code",
                            "This access code is no longer valid (expired, deactivated, or fully used).",
                        )
                    else:
                        ExamCodeRedemption.objects.create(
                            access_code=locked, student=request.user
                        )
                        locked.use_count += 1
                        locked.save(update_fields=["use_count"])
                        messages.success(
                            request, f"Access granted to: {locked.exam.title}"
                        )
                        return redirect("exams:available")
    return render(
        request,
        "exams/redeem_code.html",
        {
            "form": form,
            "already_redeemed": already_redeemed,
            "redeemed_exam": redeemed_exam,
        },
    )


@role_required(User.Role.STUDENT)
def available_exams(request):
    redeemed_ids = set(
        ExamCodeRedemption.objects.filter(student=request.user)
        .values_list("access_code__exam_id", flat=True)
    )
    # Show open-access exams + any code-gated exams the student redeemed.
    exams = [
        exam
        for exam in Exam.objects.filter(is_published=True).select_related("course")
        if exam.is_available() and (not exam.requires_access_code or exam.pk in redeemed_ids)
    ]
    return render(request, "exams/available.html", {"exams": exams})


@role_required(User.Role.STUDENT)
def start_exam(request, pk):
    exam = get_object_or_404(Exam, pk=pk, is_published=True)
    if not exam.is_available():
        messages.error(request, "This exam is not available right now.")
        return redirect("accounts:dashboard")
    if exam.requires_access_code and not ExamCodeRedemption.objects.filter(
        access_code__exam=exam, student=request.user
    ).exists():
        messages.error(request, "Redeem an access code first.")
        return redirect("exams:redeem")

    existing = get_resumable_attempt(exam, request.user)
    if existing:
        return redirect("exams:take", attempt_id=existing.pk)

    if exam.max_attempts:
        count = ExamAttempt.objects.filter(exam=exam, student=request.user).count()
        if count >= exam.max_attempts:
            messages.error(
                request,
                "Maximum attempts reached for this exam. Contact your instructor if you need another attempt.",
            )
            return redirect("accounts:dashboard")

    from apps.proctoring.models import ProctoringSession

    attempt = ExamAttempt.objects.create(
        exam=exam,
        student=request.user,
        attempt_number=ExamAttempt.objects.filter(exam=exam, student=request.user).count() + 1,
        status=ExamAttempt.Status.IN_PROGRESS,
        remaining_seconds=exam.effective_duration_minutes * 60,
    )
    ProctoringSession.objects.create(
        attempt=attempt,
        id_verification_status=ProctoringSession.IDVerificationStatus.PASSED,
        lockdown_active=True,
    )
    return redirect("exams:take", attempt_id=attempt.pk)


@role_required(User.Role.STUDENT)
def take_exam(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt, pk=attempt_id, student=request.user
    )
    if attempt.status == ExamAttempt.Status.PENDING_ID:
        from apps.proctoring.models import ProctoringSession

        attempt.status = ExamAttempt.Status.IN_PROGRESS
        attempt.save(update_fields=["status"])
        session = getattr(attempt, "proctoring_session", None)
        if session:
            session.id_verification_status = ProctoringSession.IDVerificationStatus.PASSED
            session.lockdown_active = True
            session.save(update_fields=["id_verification_status", "lockdown_active"])

    if attempt.status not in (
        ExamAttempt.Status.IN_PROGRESS,
        ExamAttempt.Status.PAUSED,
    ):
        return redirect("exams:result", attempt_id=attempt.pk)

    if attempt.exam.is_frozen and attempt.status != ExamAttempt.Status.PAUSED:
        attempt.status = ExamAttempt.Status.PAUSED
        attempt.timer_paused_at = timezone.now()
        attempt.pause_reason = ExamAttempt.PauseReason.FREEZE
        attempt.save(update_fields=["status", "timer_paused_at", "pause_reason"])

    questions = list(attempt.exam.exam_questions.select_related("question"))
    if attempt.exam.shuffle_questions:
        import random

        random.shuffle(questions)

    session = getattr(attempt, "proctoring_session", None)
    total_questions = len(questions)
    if session:
        max_strikes = session.max_strikes
        strikes_remaining = max(0, max_strikes - (session.strike_count or 0))
    else:
        max_strikes = settings.PROCTORING["MAX_STRIKES"]
        strikes_remaining = max_strikes

    return render(
        request,
        "exams/take_exam.html",
        {
            "attempt": attempt,
            "exam_questions": questions,
            "proctoring_session": session,
            "total_questions": total_questions,
            "session_code": f"KNUST-{attempt.pk:04d}-AX",
            "strikes_remaining": strikes_remaining,
        },
    )


@require_POST
@role_required(User.Role.STUDENT)
def save_answers(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
        status__in=[ExamAttempt.Status.IN_PROGRESS, ExamAttempt.Status.PAUSED],
    )
    # Pre-load valid question ids and their types for this exam so we route
    # each answer into the right column without an extra query per item.
    valid_questions = dict(
        ExamQuestion.objects.filter(exam=attempt.exam)
        .values_list("question_id", "question__question_type")
    )

    for key, value in request.POST.items():
        if not key.startswith("q_"):
            continue
        try:
            question_id = int(key[2:])
        except (TypeError, ValueError):
            continue
        qtype = valid_questions.get(question_id)
        if qtype is None:
            continue  # Question is not part of this exam — ignore.
        answer, _ = Answer.objects.get_or_create(
            attempt=attempt, question_id=question_id
        )
        if qtype in (Question.QuestionType.MCQ, Question.QuestionType.TRUE_FALSE):
            answer.selected_option = {"value": value}
            answer.text_answer = ""
        else:
            answer.text_answer = value
            answer.selected_option = None
        answer.save()
    return JsonResponse({"saved": True})


@require_POST
@role_required(User.Role.STUDENT)
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student=request.user)
    if attempt.status in (ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TERMINATED):
        return redirect("exams:result", attempt_id=attempt.pk)
    attempt.status = ExamAttempt.Status.SUBMITTED
    attempt.ended_at = timezone.now()
    attempt.save()
    grade_attempt(attempt)
    messages.success(request, "Exam submitted.")
    return redirect("exams:result", attempt_id=attempt.pk)


@require_POST
@role_required(User.Role.STUDENT)
def reconnect_exam(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
        status=ExamAttempt.Status.PAUSED,
    )
    if attempt.timer_paused_at:
        elapsed = (timezone.now() - attempt.timer_paused_at).total_seconds()
        if elapsed > attempt.disconnect_grace_seconds:
            attempt.status = ExamAttempt.Status.EXPIRED
            attempt.ended_at = timezone.now()
            attempt.save()
            grade_attempt(attempt)
            return JsonResponse({"status": "expired"})
    attempt.status = ExamAttempt.Status.IN_PROGRESS
    attempt.timer_paused_at = None
    attempt.pause_reason = ""
    attempt.save()
    return JsonResponse({"status": "resumed", "remaining_seconds": attempt.remaining_seconds})


@role_required(User.Role.STUDENT, User.Role.TEACHER, User.Role.ADMIN)
def exam_result(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related(
            "exam__course__teacher__user", "student"
        ),
        pk=attempt_id,
    )
    is_student = request.user.is_student_user
    if is_student and attempt.student_id != request.user.id:
        messages.error(request, "Not allowed.")
        return redirect("accounts:dashboard")
    if request.user.is_teacher_user:
        # Teachers may only view results for exams in their own courses.
        from django.core.exceptions import PermissionDenied

        teacher_profile = getattr(request.user, "teacher_profile", None)
        if not teacher_profile or attempt.exam.course.teacher_id != teacher_profile.pk:
            raise PermissionDenied
    # Students only see scoring if the exam allows immediate release.
    # Teachers/admins always see full results.
    show_score = (not is_student) or attempt.exam.show_results_immediately
    result = getattr(attempt, "result", None)
    answers = attempt.answers.select_related("question")

    # Proctoring notes that the teacher wrote on flagged violations. Students
    # only see entries the teacher has explicitly written a message on, so an
    # un-reviewed violation doesn't leak through as a blank row.
    proctoring_notes = []
    session = getattr(attempt, "proctoring_session", None)
    if session is not None:
        proctoring_notes = list(
            session.violations.exclude(teacher_note="")
            .order_by("created_at")
            .values(
                "violation_type",
                "teacher_note",
                "review_status",
                "reviewed_at",
                "strike_number",
            )
        )
    return render(
        request,
        "exams/result.html",
        {
            "attempt": attempt,
            "result": result,
            "answers": answers,
            "show_score": show_score,
            "proctoring_notes": proctoring_notes,
        },
    )


@role_required(User.Role.STUDENT)
def my_marks(request):
    attempts = (
        ExamAttempt.objects.filter(
            student=request.user,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TERMINATED],
        )
        .select_related("exam")
        .order_by("-started_at")
    )
    return render(request, "exams/my_marks.html", {"attempts": attempts})


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def pending_reviews(request, pk):
    exam = get_exam_for_user(request.user, pk)
    answers = Answer.objects.filter(
        attempt__exam=exam,
        review_status=Answer.ReviewStatus.PENDING_REVIEW,
    ).select_related("attempt__student", "question")
    return render(request, "exams/pending_reviews.html", {"exam": exam, "answers": answers})


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def grade_answer(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related("attempt__exam__course__teacher__user", "question"),
        pk=answer_id,
    )
    # Reuse get_exam_for_user to enforce course ownership for teachers; admins always pass.
    get_exam_for_user(request.user, answer.attempt.exam_id)
    form = ManualGradeForm(request.POST or None)
    max_marks = answer.question.marks
    if request.method == "POST" and form.is_valid():
        marks = form.cleaned_data["marks_awarded"]
        if marks > max_marks:
            messages.error(request, f"Marks cannot exceed {max_marks}.")
        else:
            ManualGrade.objects.update_or_create(
                answer=answer,
                defaults={
                    "graded_by": request.user,
                    "marks_awarded": marks,
                    "feedback": form.cleaned_data["feedback"],
                },
            )
            answer.marks_awarded = marks
            answer.is_correct = marks > 0
            answer.review_status = Answer.ReviewStatus.MANUALLY_GRADED
            answer.save()

            attempt = answer.attempt
            result, _ = Result.objects.get_or_create(attempt=attempt)
            manual_total = sum(
                a.marks_awarded or 0
                for a in attempt.answers.filter(
                    review_status=Answer.ReviewStatus.MANUALLY_GRADED
                )
            )
            result.manual_score = manual_total
            result.total_score = result.auto_score + manual_total
            result.save()

            pending = attempt.answers.filter(
                review_status=Answer.ReviewStatus.PENDING_REVIEW
            ).exists()
            if not pending:
                attempt.grading_status = ExamAttempt.GradingStatus.COMPLETE
                attempt.score = result.total_score
                attempt.percentage = (
                    (result.total_score / result.max_score * 100)
                    if result.max_score
                    else 0
                )
                attempt.passed = result.total_score >= attempt.exam.passing_marks
                result.finalized_at = timezone.now()
                result.save()
            attempt.save()
            messages.success(request, "Answer graded.")
            return redirect("exams:pending_reviews", pk=attempt.exam_id)
    return render(
        request,
        "exams/grade_answer.html",
        {"form": form, "answer": answer, "max_marks": max_marks},
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_bank_list(request):
    banks = (
        QuestionBank.objects.select_related("course")
        .annotate(question_count=Count("questions"))
        .order_by("-created_at")
    )
    if not request.user.is_admin_user:
        banks = banks.filter(course__teacher__user=request.user)
    return render_portal(
        request,
        "partials/portal/question_bank_list.html",
        {"banks": banks, "portal_nav": "banks"},
        page_title="Question Banks",
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_bank_create(request):
    if request.user.is_admin_user:
        return redirect("exams:question_banks")
    form = QuestionBankForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        bank = form.save(commit=False)
        bank.created_by = request.user
        bank.save()
        messages.success(request, "Question bank created. Add questions manually or import a CSV.")
        return redirect("exams:question_bank_builder", bank_id=bank.pk)
    return render(
        request,
        "exams/question_bank_create.html",
        {"form": form, "portal_nav": "banks", "qb_tab": "builder"},
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_import_sample(_request):
    sample_path = Path(settings.BASE_DIR) / "static" / "samples" / "question_import_sample.csv"
    return FileResponse(
        sample_path.open("rb"),
        as_attachment=True,
        filename="question_import_sample.csv",
        content_type="text/csv",
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_bank_detail(request, bank_id):
    return redirect("exams:question_bank_builder", bank_id=bank_id)


def _create_blank_question(bank):
    return Question.objects.create(
        question_bank=bank,
        text="Enter your question here…",
        question_type=Question.QuestionType.MCQ,
        options=[
            {"key": "A", "label": "Option A"},
            {"key": "B", "label": "Option B"},
            {"key": "C", "label": "Option C"},
            {"key": "D", "label": "Option D"},
        ],
        correct_answer={"value": "A"},
    )


def _builder_context(bank, questions, active_question, form=None):
    sections = {}
    for q in questions:
        sections.setdefault(q.section, []).append(q)
    total = questions.count() if hasattr(questions, "count") else len(list(questions))
    complete = sum(1 for q in questions if q.is_complete)
    next_question = None
    prev_question = None
    if active_question:
        next_question = questions.filter(order__gt=active_question.order).first()
        prev_question = questions.filter(order__lt=active_question.order).order_by("-order").first()
    return {
        "bank": bank,
        "questions": questions,
        "sections": sections,
        "active_question": active_question,
        "next_question": next_question,
        "prev_question": prev_question,
        "form": form or (QuestionForm(instance=active_question) if active_question else None),
        "total_questions": total,
        "complete_count": complete,
        "total_marks": bank.total_marks,
        "portal_nav": "banks",
        "qb_tab": "builder",
    }


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_bank_builder(request, bank_id):
    if request.user.is_admin_user:
        return redirect("exams:question_banks")
    bank = get_bank_for_user(request.user, bank_id)
    questions = bank.questions.all()
    qid = request.GET.get("q")
    active = questions.filter(pk=qid).first() if qid else questions.first()

    if request.method == "POST":
        action = request.POST.get("action", "save")
        if action == "add_question":
            question = _create_blank_question(bank)
            messages.success(request, f"Question Q{question.order} created.")
            return redirect(
                f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={question.pk}"
            )

        if active:
            form = QuestionForm(request.POST, instance=active)
            if form.is_valid():
                form.save()
                messages.success(request, f"Question Q{active.order} saved.")
                if action == "save_next":
                    next_q = questions.filter(order__gt=active.order).first()
                    if next_q:
                        return redirect(
                            f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={next_q.pk}"
                        )
                return redirect(
                    f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={active.pk}"
                )
        else:
            form = None
    else:
        form = QuestionForm(instance=active) if active else None

    ctx = _builder_context(bank, questions, active, form)
    return render(request, "exams/question_bank_builder.html", ctx)


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_bank_library(request, bank_id):
    bank = get_bank_for_user(request.user, bank_id)
    questions = bank.questions.all()
    return render(
        request,
        "exams/question_bank_library.html",
        {"bank": bank, "questions": questions, "portal_nav": "banks", "qb_tab": "library"},
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_add(request, bank_id):
    bank = get_bank_for_user(request.user, bank_id)
    question = _create_blank_question(bank)
    messages.success(request, f"Question Q{question.order} created.")
    return redirect(
        f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={question.pk}"
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_edit(request, bank_id, question_id):
    bank = get_bank_for_user(request.user, bank_id)
    question = get_question_for_user(request.user, bank_id, question_id)
    return redirect(
        f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={question.pk}"
    )


@require_POST
@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_delete(request, bank_id, question_id):
    bank = get_bank_for_user(request.user, bank_id)
    question = get_question_for_user(request.user, bank_id, question_id)
    if question.exam_questions.exists():
        messages.error(request, "Cannot delete — question is used in an exam. Remove it from exams first.")
        return redirect(f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={question.pk}")
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("exams:question_bank_builder", bank_id=bank.pk)


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def question_bank_import(request, bank_id):
    bank = get_bank_for_user(request.user, bank_id)
    form = QuestionCSVImportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        created, errors = import_questions_from_csv(bank, form.cleaned_data["csv_file"])
        if created:
            messages.success(request, f"Imported {created} question(s).")
        for err in errors[:10]:
            messages.error(request, err)
        if len(errors) > 10:
            messages.error(request, f"…and {len(errors) - 10} more errors.")
        if created and not errors:
            first_q = bank.questions.order_by("order", "pk").first()
            if first_q:
                return redirect(
                    f"{reverse('exams:question_bank_builder', kwargs={'bank_id': bank.pk})}?q={first_q.pk}"
                )
            return redirect("exams:question_bank_builder", bank_id=bank.pk)
    return render(
        request,
        "exams/question_bank_import.html",
        {"form": form, "bank": bank, "portal_nav": "banks", "qb_tab": "import"},
    )


def _exam_question_choices(exam):
    existing_ids = set(exam.exam_questions.values_list("question_id", flat=True))
    # Single query joining the bank title — avoid the per-bank queryset evaluation.
    rows = (
        Question.objects.filter(question_bank__course=exam.course)
        .exclude(pk__in=existing_ids)
        .select_related("question_bank")
        .values_list("pk", "text", "question_bank__title")
    )
    choices = []
    for pk, text, bank_title in rows:
        label = f"[{bank_title}] {text[:70]}{'…' if len(text) > 70 else ''}"
        choices.append((str(pk), label))
    return choices


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def exam_questions(request, pk):
    exam = get_exam_for_user(request.user, pk)
    exam_question_rows = list(
        exam.exam_questions.select_related("question", "question__question_bank").order_by("order", "pk")
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            ids = request.POST.getlist("question_ids")
            if ids:
                max_order = exam.exam_questions.aggregate(m=Max("order"))["m"] or 0
                existing = set(exam.exam_questions.values_list("question_id", flat=True))
                valid_ids = set()
                for bank in QuestionBank.objects.filter(course=exam.course):
                    valid_ids.update(bank.questions.values_list("pk", flat=True))
                added = 0
                for qid in ids:
                    qid_int = int(qid)
                    if qid_int not in valid_ids or qid_int in existing:
                        continue
                    max_order += 1
                    ExamQuestion.objects.create(exam=exam, question_id=qid_int, order=max_order)
                    existing.add(qid_int)
                    added += 1
                messages.success(request, f"Added {added} question(s) to the exam.")
            else:
                messages.warning(request, "Select at least one question to add.")
        elif action == "remove":
            eq_id = request.POST.get("exam_question_id")
            if eq_id:
                exam.exam_questions.filter(pk=eq_id).delete()
                messages.success(request, "Question removed from exam.")
        elif action == "reorder":
            order_raw = request.POST.get("order", "")
            order_ids = [x.strip() for x in order_raw.split(",") if x.strip()]
            with transaction.atomic():
                for index, eq_id in enumerate(order_ids):
                    exam.exam_questions.filter(pk=eq_id).update(order=index)
            messages.success(request, "Question order updated.")
        return redirect("exams:exam_questions", pk=exam.pk)

    add_form = ExamQuestionAddForm(choices=_exam_question_choices(exam))
    banks = QuestionBank.objects.filter(course=exam.course).annotate(
        question_count=Count("questions")
    )
    return render(
        request,
        "exams/exam_questions.html",
        {
            "exam": exam,
            "exam_question_rows": exam_question_rows,
            "add_form": add_form,
            "banks": banks,
            "portal_nav": "exams",
        },
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def exam_preview(request, pk):
    exam = get_exam_for_user(request.user, pk)
    exam_questions = list(exam.exam_questions.select_related("question").order_by("order", "pk"))
    return render(
        request,
        "exams/exam_preview.html",
        {
            "exam": exam,
            "exam_questions": exam_questions,
            "total_questions": len(exam_questions),
            "portal_nav": "exams",
        },
    )


@role_required(User.Role.ADMIN)
def admin_pending_exams(request):
    from apps.accounts.views import _admin_sidebar_context

    exams = (
        Exam.objects.filter(approval_status=Exam.ApprovalStatus.PENDING)
        .select_related("course", "course__teacher__user", "created_by")
        .annotate(question_count=Count("exam_questions"))
        .order_by("submitted_for_approval_at")
    )
    sidebar = _admin_sidebar_context()
    return render_portal(
        request,
        "partials/portal/admin_pending_exams.html",
        {
            "portal_nav": "exam_approvals",
            "exams": exams,
            "notification_count": sidebar["pending_teachers"] + exams.count(),
        },
        page_title="Exam Approvals",
    )


@role_required(User.Role.ADMIN)
def admin_exam_review(request, pk):
    from apps.accounts.views import _admin_sidebar_context

    exam = get_object_or_404(
        Exam.objects.select_related("course", "course__teacher__user", "created_by"),
        pk=pk,
    )
    exam_questions = exam.exam_questions.select_related("question").order_by("order", "pk")
    add_time_form = AdminAddTimeForm()
    freeze_form = AdminFreezeForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            exam.approval_status = Exam.ApprovalStatus.APPROVED
            exam.approved_by = request.user
            exam.approved_at = timezone.now()
            exam.rejection_reason = ""
            exam.save()
            messages.success(request, f"Approved exam: {exam.title}")
            return redirect("exams:admin_pending_exams")
        if action == "reject":
            exam.approval_status = Exam.ApprovalStatus.REJECTED
            exam.rejection_reason = request.POST.get("rejection_reason", "Rejected by administrator.")
            exam.is_published = False
            exam.save()
            messages.info(request, f"Rejected exam: {exam.title}")
            return redirect("exams:admin_pending_exams")
        if action == "freeze":
            freeze_form = AdminFreezeForm(request.POST)
            if freeze_form.is_valid():
                freeze_exam(exam, freeze_form.cleaned_data["reason"])
                messages.warning(request, "Exam frozen. Active attempts paused.")
        elif action == "unfreeze":
            unfreeze_exam(exam)
            messages.success(request, "Exam unfrozen.")
        elif action == "add_time":
            add_time_form = AdminAddTimeForm(request.POST)
            if add_time_form.is_valid():
                add_exam_time(exam, add_time_form.cleaned_data["minutes"])
                messages.success(
                    request,
                    f"Added {add_time_form.cleaned_data['minutes']} minutes to the exam.",
                )
        return redirect("exams:admin_exam_review", pk=exam.pk)

    sidebar = _admin_sidebar_context()
    return render_portal(
        request,
        "partials/portal/admin_exam_review.html",
        {
            "portal_nav": "exam_approvals",
            "back_url": reverse("exams:admin_pending_exams"),
            "dashboard_url": reverse("accounts:dashboard"),
            "exam": exam,
            "exam_questions": exam_questions,
            "add_time_form": add_time_form,
            "freeze_form": freeze_form,
            "notification_count": sidebar["pending_teachers"] + Exam.objects.filter(
                approval_status=Exam.ApprovalStatus.PENDING
            ).count(),
        },
        page_title=f"Review Exam — {exam.title}",
    )
