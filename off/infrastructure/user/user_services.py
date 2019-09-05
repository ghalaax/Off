from django.conf import settings
from django.contrib.auth.models import User
from off.infrastructure import constants
from django.db import transaction


class Services:

    @staticmethod
    @transaction.atomic
    def CreateLightUser(last_name, first_name, username=None, email=None):
        email = email or Services.createDefaultUserEmail(last_name, first_name)
        user = User(username=(username or email).lower(), email=email.lower(),
                    first_name=first_name, last_name=last_name)
        user.set_unusable_password()
        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def UpdateUser(user, last_name, first_name, username=None, email=None):
        email = email or Services.createDefaultUserEmail(last_name, first_name)
        user.username = (username or email).lower()
        user.email=email.lower()
        user.first_name=first_name
        user.last_name=last_name
        user.save()
        return user
    
    @staticmethod
    def emailExists(last_name, first_name, email=None, pk=None):
        email = email or Services.createDefaultUserEmail(last_name, first_name)
        try:
            o = User.objects.exclude(id=pk).get(email=email)
            return True
        except User.DoesNotExist:
            return False

    @staticmethod
    def createDefaultUserEmail(last_name, first_name, default_user_email_pattern='%(first_name)s.%(last_name)s@%(domain_name)s'):
        domain_name = constants.DOMAIN_NAME
        if hasattr(settings, 'DEFAULT_EMAIL_DOMAIN_NAME') and settings.DEFAULT_EMAIL_DOMAIN_NAME:
            domain_name = settings.DEFAULT_EMAIL_DOMAIN_NAME
        data = {'last_name': last_name,
                'first_name': first_name, 'domain_name': domain_name}
        return default_user_email_pattern % data

    @staticmethod
    def getUserByUsername(username):
        return User.objects.get(username=username)
