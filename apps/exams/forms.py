from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.courses.models import Course

from .models import Exam, ExamAccessCode, ExamQuestion, Question, QuestionBank

DATETIME_LOCAL_FMT = "%Y-%m-%dT%H:%M"


class QuestionBankForm(forms.ModelForm):
    class Meta:
        model = QuestionBank
        fields = ("course", "title")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and not user.is_admin_user:
            self.fields["course"].queryset = Course.objects.filter(teacher__user=user)
        self.fields["course"].widget.attrs.update({"class": "qb-select"})
        self.fields["title"].widget.attrs.update(
            {"class": "qb-input", "placeholder": "e.g. Midterm II — AI & Expert Systems"}
        )


class QuestionForm(forms.ModelForm):
    correct_value = forms.CharField(
        max_length=255,
        label="Correct answer",
        required=False,
        widget=forms.HiddenInput(),
    )
    tags_text = forms.CharField(
        required=False,
        label="Module tags",
        help_text="Comma-separated tags",
        widget=forms.TextInput(attrs={"class": "qb-input", "placeholder": "Expert Systems, Inference"}),
    )

    class Meta:
        model = Question
        fields = (
            "text",
            "question_type",
            "section",
            "marks",
            "explanation",
            "difficulty",
            "blooms_level",
            "is_complete",
        )
        widgets = {
            "text": forms.Textarea(
                attrs={"rows": 5, "class": "qb-textarea", "id": "qb-question-text"}
            ),
            "section": forms.TextInput(attrs={"class": "qb-input"}),
            "marks": forms.NumberInput(attrs={"class": "qb-input", "step": "1", "min": "1"}),
            "explanation": forms.Textarea(
                attrs={"rows": 2, "class": "qb-textarea", "id": "qb-explanation"}
            ),
            "blooms_level": forms.TextInput(attrs={"class": "qb-input"}),
            "difficulty": forms.Select(attrs={"class": "qb-select"}),
            "question_type": forms.Select(attrs={"class": "qb-select", "id": "id_question_type"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            ca = self.instance.correct_answer or {}
            self.fields["correct_value"].initial = ca.get("value") or ca.get("reference", "")
        if self.instance.pk and self.instance.module_tags:
            self.fields["tags_text"].initial = ", ".join(self.instance.module_tags)

    def _parse_option_labels(self):
        labels = []
        index = 0
        while f"option_label_{index}" in self.data:
            label = self.data.get(f"option_label_{index}", "").strip()
            if label:
                labels.append(label)
            index += 1
        return labels

    def clean(self):
        cleaned_data = super().clean()
        qtype = cleaned_data.get("question_type")

        if qtype == Question.QuestionType.MCQ:
            labels = self._parse_option_labels()
            if len(labels) < 2:
                raise forms.ValidationError("Add at least two answer options.")
            cleaned_data["_option_labels"] = labels
            try:
                correct_index = int(self.data.get("correct_option_index", 0))
            except (TypeError, ValueError):
                correct_index = 0
            correct_index = max(0, min(correct_index, len(labels) - 1))
            cleaned_data["correct_value"] = chr(65 + correct_index)

        elif qtype == Question.QuestionType.TRUE_FALSE:
            correct = (self.data.get("correct_value") or "").strip().lower()
            if correct not in ("true", "false"):
                raise forms.ValidationError("Select True or False as the correct answer.")
            cleaned_data["correct_value"] = correct

        else:
            reference = (self.data.get("correct_reference") or cleaned_data.get("correct_value") or "").strip()
            if not reference:
                raise forms.ValidationError("Enter a reference answer for short-answer questions.")
            cleaned_data["correct_value"] = reference

        return cleaned_data

    def save(self, commit=True):
        question = super().save(commit=False)
        qtype = self.cleaned_data["question_type"]
        if qtype == Question.QuestionType.MCQ:
            labels = self.cleaned_data.get("_option_labels", [])
            question.options = [{"key": chr(65 + i), "label": label} for i, label in enumerate(labels)]
            question.correct_answer = {"value": self.cleaned_data["correct_value"]}
        elif qtype == Question.QuestionType.TRUE_FALSE:
            question.options = [{"key": "true", "label": "True"}, {"key": "false", "label": "False"}]
            question.correct_answer = {"value": self.cleaned_data["correct_value"].lower()}
        else:
            question.options = []
            question.correct_answer = {"reference": self.cleaned_data["correct_value"]}
        tags = [t.strip() for t in self.cleaned_data.get("tags_text", "").split(",") if t.strip()]
        question.module_tags = tags
        if commit:
            question.save()
        return question


class AdminAddTimeForm(forms.Form):
    minutes = forms.IntegerField(min_value=1, max_value=180, initial=15, label="Minutes to add")


class AdminFreezeForm(forms.Form):
    reason = forms.CharField(
        max_length=255,
        initial="System outage — exam paused by administrator",
        widget=forms.TextInput(attrs={"class": "qb-input"}),
    )


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = (
            "course",
            "title",
            "description",
            "duration_minutes",
            "total_marks",
            "passing_marks",
            "max_attempts",
            "shuffle_questions",
            "show_results_immediately",
            "requires_access_code",
            "strictness_level",
            "available_from",
            "available_until",
        )
        widgets = {
            "available_from": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "qb-input"},
                format=DATETIME_LOCAL_FMT,
            ),
            "available_until": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "qb-input"},
                format=DATETIME_LOCAL_FMT,
            ),
            "strictness_level": forms.RadioSelect(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.is_admin_user:
            self.fields["course"].queryset = Course.objects.filter(teacher__user=user)
        for name in ("available_from", "available_until"):
            field = self.fields[name]
            field.input_formats = [DATETIME_LOCAL_FMT]
        self.fields["available_from"].help_text = (
            "When students can start the exam (local server time, UTC in dev)."
        )
        self.fields["available_until"].help_text = (
            "Last time a student may begin the exam. This is the availability window end — "
            "not the same as per-attempt duration."
        )
        if self.instance.pk:
            for name in ("available_from", "available_until"):
                value = getattr(self.instance, name)
                if value:
                    self.initial[name] = timezone.localtime(value).strftime(DATETIME_LOCAL_FMT)

    def _aware_local(self, value):
        if value is None:
            return None
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def clean_available_from(self):
        return self._aware_local(self.cleaned_data.get("available_from"))

    def clean_available_until(self):
        until = self._aware_local(self.cleaned_data.get("available_until"))
        start = self.cleaned_data.get("available_from")
        if start is None and self.instance.pk:
            start = self.instance.available_from
        if start and until and until <= start:
            raise ValidationError("Available until must be after available from.")
        return until


class RedeemCodeForm(forms.Form):
    code = forms.CharField(max_length=16, label="Exam Access Code")


class AccessCodeForm(forms.ModelForm):
    class Meta:
        model = ExamAccessCode
        fields = ("max_uses", "expires_at")
        widgets = {"expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class ManualGradeForm(forms.Form):
    marks_awarded = forms.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    feedback = forms.CharField(widget=forms.Textarea, required=False)


class QuestionCSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV file",
        help_text="UTF-8 .csv file with columns: type, text, correct, marks (see format guide below).",
        widget=forms.FileInput(attrs={"accept": ".csv,text/csv"}),
    )


class ExamQuestionAddForm(forms.Form):
    question_ids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Questions to add",
    )

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["question_ids"].choices = choices or []


class ExamQuestionOrderForm(forms.Form):
    order = forms.CharField(
        widget=forms.HiddenInput(),
        help_text="Comma-separated ExamQuestion IDs in display order",
    )
