from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """Normalize email and enforce lowercase storage for uniqueness checks."""

    def normalize_email(self, email):
        email = super().normalize_email(email)
        return email.lower() if email else email

    def create_user(self, username, email=None, password=None, **extra_fields):
        email = self.normalize_email(email) if email else email
        extra_fields.pop("email", None)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        email = self.normalize_email(email) if email else email
        extra_fields.pop("email", None)
        return super().create_superuser(username, email, password, **extra_fields)
