from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

    objects = UserManager()

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_teacher_user(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student_user(self):
        return self.role == self.Role.STUDENT


class TeacherProfile(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    approval_status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_teachers"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    staff_id_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    id_proof_image = models.ImageField(upload_to="staff_id_proofs/", blank=True, null=True)
    id_card_verified = models.BooleanField(default=False)
    id_verification_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.username}"


class StudentProfile(models.Model):
    class IDReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending Admin Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id_number = models.CharField(max_length=50, unique=True)
    programme = models.CharField(max_length=255, blank=True)
    id_proof_image = models.ImageField(upload_to="id_proofs/", blank=True, null=True)
    face_embedding = models.JSONField(default=list, blank=True)
    id_card_verified = models.BooleanField(default=False)
    id_verification_data = models.JSONField(default=dict, blank=True)
    id_review_status = models.CharField(
        max_length=20,
        choices=IDReviewStatus.choices,
        default=IDReviewStatus.APPROVED,
        help_text="Set to PENDING when OCR fails and the student needs a manual admin review.",
    )
    id_review_notes = models.TextField(blank=True)
    id_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_student_ids",
    )
    id_reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username}"

    @property
    def needs_id_review(self):
        return self.id_review_status == self.IDReviewStatus.PENDING


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    def __str__(self):
        return f"Admin: {self.user.get_full_name() or self.user.username}"
