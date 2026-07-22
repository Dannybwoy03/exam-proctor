import base64
import binascii

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from ml.id_verification.knust_validator import verify_knust_staff_id, verify_knust_student_id

from .models import AdminProfile, StudentProfile, TeacherProfile, User

FACE_SCAN_MAX_BYTES = 5_000_000  # decoded JPEG from the registration webcam scan


def decode_face_scan(data_url: str) -> bytes:
    """Decode a ``data:image/...;base64,`` URL from the webcam scan.

    Raises ValidationError on malformed or oversized payloads.
    """
    payload = data_url.strip()
    if payload.startswith("data:"):
        _, _, payload = payload.partition(",")
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError):
        raise ValidationError("Face scan data is invalid. Please retake the scan.")
    if not raw:
        raise ValidationError("Face scan is empty. Please retake the scan.")
    if len(raw) > FACE_SCAN_MAX_BYTES:
        raise ValidationError("Face scan image is too large. Please retake the scan.")
    return raw


class RegistrationValidationMixin:
    """Shared uniqueness checks for student and teacher registration."""

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"].strip())
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email


class StudentRegistrationForm(RegistrationValidationMixin, UserCreationForm):
    student_id_number = forms.CharField(
        max_length=50,
        label="Student / Index Number",
        help_text="Must match the number printed on your KNUST ID card.",
    )
    programme = forms.CharField(
        max_length=255,
        label="Programme of Study",
        help_text="e.g. BSc Computer Science — must match your ID card.",
    )
    id_proof_image = forms.ImageField(
        label="KNUST Student ID Card (photo)",
        help_text="Upload a clear photo of your official KNUST student ID.",
    )
    face_scan_data = forms.CharField(
        label="Face Scan",
        widget=forms.HiddenInput(),
        error_messages={"required": "Complete the face scan with your webcam."},
        help_text="Captured live with your webcam. Used to verify your identity before exams.",
    )
    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "username",
                "email",
                "first_name",
                "last_name",
                "student_id_number",
                "programme",
                "id_proof_image",
                "face_scan_data",
                "phone",
                "password1",
                "password2",
            ]
        )

    def clean_student_id_number(self):
        student_id = self.cleaned_data["student_id_number"].strip()
        if StudentProfile.objects.filter(student_id_number__iexact=student_id).exists():
            raise ValidationError("This student ID is already registered.")
        return student_id

    def clean_face_scan_data(self):
        """Decode the webcam scan and compute the ArcFace embedding.

        Hard-fails when the model is available but finds no face (the scan is
        live, so the student can simply retake it). Soft-fails to an empty
        embedding when insightface is not installed, mirroring the OCR
        soft-fail policy.
        """
        from ml.face_id.service import embed_face, face_id_available

        scan_bytes = decode_face_scan(self.cleaned_data["face_scan_data"])
        self._face_scan_bytes = scan_bytes
        self._face_embedding = []

        if not face_id_available():
            return self.cleaned_data["face_scan_data"]

        embedding = embed_face(scan_bytes)
        if embedding is None:
            raise ValidationError(
                "No face detected in your scan. Face the camera in good lighting and retake it."
            )
        self._face_embedding = embedding
        return self.cleaned_data["face_scan_data"]

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("id_proof_image")
        if not image:
            return cleaned_data

        result = verify_knust_student_id(
            image,
            student_id_number=cleaned_data.get("student_id_number", ""),
            first_name=cleaned_data.get("first_name", ""),
            last_name=cleaned_data.get("last_name", ""),
            programme=cleaned_data.get("programme", ""),
        )
        self._id_verification_result = result
        # Soft-fail: do not raise on OCR mismatch. The account is created with
        # id_review_status=PENDING and an admin reviews the upload manually.
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.email = User.objects.normalize_email(user.email)
        verification = getattr(self, "_id_verification_result", None)
        ocr_passed = bool(verification and verification.is_valid)
        if commit:
            scan_bytes = getattr(self, "_face_scan_bytes", None)
            if scan_bytes:
                user.profile_photo = ContentFile(scan_bytes, name="face_scan.jpg")
            user.save()
            StudentProfile.objects.create(
                user=user,
                student_id_number=self.cleaned_data["student_id_number"].strip(),
                programme=self.cleaned_data["programme"],
                id_proof_image=self.cleaned_data["id_proof_image"],
                face_embedding=getattr(self, "_face_embedding", []),
                id_card_verified=ocr_passed,
                id_review_status=(
                    StudentProfile.IDReviewStatus.APPROVED
                    if ocr_passed
                    else StudentProfile.IDReviewStatus.PENDING
                ),
                id_verification_data={
                    "matched_fields": verification.matched_fields if verification else {},
                    "ocr_preview": (verification.ocr_text[:500] if verification else ""),
                    "ocr_errors": verification.errors if verification else [],
                    "ocr_warnings": verification.warnings if verification else [],
                    "ocr_passed": ocr_passed,
                },
            )
        return user


class TeacherRegistrationForm(RegistrationValidationMixin, UserCreationForm):
    staff_id_number = forms.CharField(
        max_length=50,
        label="Staff ID Number",
        help_text="Must match the number printed on your KNUST staff ID card.",
    )
    department = forms.CharField(
        max_length=255,
        label="Department",
        help_text="Must match your department as shown on your staff ID.",
    )
    id_proof_image = forms.ImageField(
        label="KNUST Staff ID Card (photo)",
        help_text="Upload a clear photo of your official KNUST staff ID.",
    )
    profile_photo = forms.ImageField(
        label="Profile Photo (face)",
        required=False,
        help_text="Optional profile photo.",
    )
    qualification = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile_photo",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "username",
                "email",
                "first_name",
                "last_name",
                "staff_id_number",
                "department",
                "id_proof_image",
                "profile_photo",
                "qualification",
                "phone",
                "password1",
                "password2",
            ]
        )

    def clean_staff_id_number(self):
        staff_id = self.cleaned_data["staff_id_number"].strip()
        if TeacherProfile.objects.filter(staff_id_number__iexact=staff_id).exists():
            raise ValidationError("This staff ID is already registered.")
        return staff_id

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("id_proof_image")
        if not image:
            return cleaned_data

        result = verify_knust_staff_id(
            image,
            staff_id_number=cleaned_data.get("staff_id_number", ""),
            first_name=cleaned_data.get("first_name", ""),
            last_name=cleaned_data.get("last_name", ""),
            department=cleaned_data.get("department", ""),
        )
        self._id_verification_result = result
        # Soft-fail: do not raise. Admin reviews the OCR result during teacher approval.
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.email = User.objects.normalize_email(user.email)
        verification = getattr(self, "_id_verification_result", None)
        ocr_passed = bool(verification and verification.is_valid)
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                staff_id_number=self.cleaned_data["staff_id_number"].strip(),
                department=self.cleaned_data["department"],
                qualification=self.cleaned_data.get("qualification", ""),
                id_proof_image=self.cleaned_data["id_proof_image"],
                id_card_verified=ocr_passed,
                id_verification_data={
                    "matched_fields": verification.matched_fields if verification else {},
                    "ocr_preview": (verification.ocr_text[:500] if verification else ""),
                    "ocr_errors": verification.errors if verification else [],
                    "ocr_warnings": verification.warnings if verification else [],
                    "ocr_passed": ocr_passed,
                },
            )
        return user


class AdminCreateUserForm(RegistrationValidationMixin, UserCreationForm):
    """Admin-provisioned user creation. No ID/OCR — admin vouches for the account."""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )

    role = User.Role.STUDENT  # subclasses override

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.role
        user.email = User.objects.normalize_email(user.email)
        if commit:
            user.save()
            self.create_profile(user)
        return user

    def create_profile(self, user):
        raise NotImplementedError


class AdminCreateStudentForm(AdminCreateUserForm):
    role = User.Role.STUDENT

    student_id_number = forms.CharField(
        max_length=50,
        label="Student / Index Number",
        help_text="KNUST index number. Required for exam access.",
    )
    programme = forms.CharField(max_length=255, label="Programme", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "username",
                "email",
                "first_name",
                "last_name",
                "student_id_number",
                "programme",
                "phone",
                "password1",
                "password2",
            ]
        )

    def clean_student_id_number(self):
        sid = self.cleaned_data["student_id_number"].strip()
        if StudentProfile.objects.filter(student_id_number__iexact=sid).exists():
            raise ValidationError("This student ID is already registered.")
        return sid

    def create_profile(self, user):
        StudentProfile.objects.create(
            user=user,
            student_id_number=self.cleaned_data["student_id_number"].strip(),
            programme=self.cleaned_data.get("programme", ""),
            id_card_verified=True,
            id_review_status=StudentProfile.IDReviewStatus.APPROVED,
            id_verification_data={"provisioned_by_admin": True},
        )


class AdminCreateTeacherForm(AdminCreateUserForm):
    role = User.Role.TEACHER

    staff_id_number = forms.CharField(
        max_length=50,
        label="Staff ID Number",
        help_text="KNUST staff ID. Used on teacher-issued exam materials.",
    )
    department = forms.CharField(max_length=255, label="Department", required=False)
    qualification = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "username",
                "email",
                "first_name",
                "last_name",
                "staff_id_number",
                "department",
                "qualification",
                "phone",
                "password1",
                "password2",
            ]
        )

    def clean_staff_id_number(self):
        sid = self.cleaned_data["staff_id_number"].strip()
        if TeacherProfile.objects.filter(staff_id_number__iexact=sid).exists():
            raise ValidationError("This staff ID is already registered.")
        return sid

    def create_profile(self, user):
        TeacherProfile.objects.create(
            user=user,
            staff_id_number=self.cleaned_data["staff_id_number"].strip(),
            department=self.cleaned_data.get("department", ""),
            qualification=self.cleaned_data.get("qualification", ""),
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
            id_card_verified=True,
            id_verification_data={"provisioned_by_admin": True},
        )
        # NB: approved_at / approved_by are filled by the view (it has request.user).


class AdminCreateAdminForm(AdminCreateUserForm):
    """Restricted to superusers; creates another admin user."""

    role = User.Role.ADMIN

    def create_profile(self, user):
        AdminProfile.objects.create(user=user)


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or email",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Username or email",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "The username/email or password you entered is incorrect. Please try again.",
        "inactive": "This account is inactive. Contact the administrator.",
    }

