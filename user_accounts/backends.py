from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from user_accounts.models import Account


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
            if user.check_password(raw_password=password):
                return user
        except user_model.DoesNotExist:
            return None
