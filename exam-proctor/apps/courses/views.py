from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import User
from apps.accounts.portal import render_portal

from .forms import CourseForm
from .models import Course


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def course_list(request):
    if request.user.is_admin_user:
        courses = Course.objects.select_related("teacher__user").all()
    else:
        courses = Course.objects.filter(teacher__user=request.user)
    return render_portal(
        request,
        "partials/portal/course_list.html",
        {"courses": courses, "portal_nav": "courses"},
        page_title="Courses",
    )


@role_required(User.Role.TEACHER, User.Role.ADMIN)
def course_create(request):
    form = CourseForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course created.")
        return redirect("courses:list")
    return render(request, "courses/course_form.html", {"form": form, "title": "Create Course", "portal_nav": "courses"})


@role_required(User.Role.STUDENT)
def student_materials(request, course_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    # Enrollment proxy: a student is "in" a course iff they have redeemed an
    # access code for any of its exams. This mirrors the design doc's decision
    # to use access codes as the only enrollment signal.
    from apps.exams.models import ExamCodeRedemption

    enrolled = ExamCodeRedemption.objects.filter(
        student=request.user, access_code__exam__course=course
    ).exists()
    if not enrolled:
        messages.error(
            request,
            "Redeem an access code for one of this course's exams to view its materials.",
        )
        return redirect("exams:redeem")
    materials = course.materials.all()
    return render(
        request,
        "courses/student_materials.html",
        {"course": course, "materials": materials},
    )
