from django import forms

from apps.accounts.models import TeacherProfile

from .models import Course


class CourseForm(forms.ModelForm):
    """Course creation/edit form.

    - Teachers: ``teacher`` field is hidden; course is bound to their own
      ``teacher_profile``.
    - Admins: ``teacher`` field is required (admins don't own courses
      themselves and must assign one to an approved teacher).
    """

    teacher = forms.ModelChoiceField(
        queryset=TeacherProfile.objects.none(),
        required=False,
        help_text="The teacher who owns this course.",
    )

    class Meta:
        model = Course
        fields = ("code", "title", "description", "is_active")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user is not None and getattr(user, "is_admin_user", False):
            self.fields["teacher"].queryset = (
                TeacherProfile.objects.filter(
                    approval_status=TeacherProfile.ApprovalStatus.APPROVED
                )
                .select_related("user")
                .order_by("user__last_name", "user__first_name")
            )
            self.fields["teacher"].required = True
            if self.instance and self.instance.pk:
                self.fields["teacher"].initial = self.instance.teacher_id
        else:
            self.fields.pop("teacher", None)

    def save(self, commit=True):
        course = super().save(commit=False)
        if self.user is not None and getattr(self.user, "is_admin_user", False):
            course.teacher = self.cleaned_data["teacher"]
        elif not course.pk:
            profile = getattr(self.user, "teacher_profile", None)
            if profile is None:
                raise ValueError(
                    "CourseForm requires the requesting user to have a teacher_profile."
                )
            course.teacher = profile
        if commit:
            course.save()
        return course
