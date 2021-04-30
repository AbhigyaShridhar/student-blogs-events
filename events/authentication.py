#Overriding the authentiaction backend for email addresses
from django.contrib.auth.backends import BaseBackend
from events.models import User

class authBackend(BaseBackend):
    def authenticate(self, request, username, password):
        try:
            user = User.objects.get(email=username)
            success = user.check_password(password)
            if success:
                return user
        except User.DoesNotExist:
            user = None
        return user

    def get_user(self, uid):
        try:
            return User.objects.get(pk=uid)
        except:
            return None
