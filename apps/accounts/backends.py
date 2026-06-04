from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailOrUsernameBackend(ModelBackend):
    """Allow sign-in with username or email (case-insensitive)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None or password is None:
            return None

        login = username.strip()
        user = None
        if "@" in login:
            try:
                user = UserModel.objects.get(email__iexact=login)
            except UserModel.DoesNotExist:
                UserModel().set_password(password)
                return None
        else:
            try:
                user = UserModel.objects.get(username__iexact=login)
            except UserModel.DoesNotExist:
                UserModel().set_password(password)
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
