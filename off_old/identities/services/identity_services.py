from django.db import transaction
from off.identities.models import Identity
from django.utils.crypto import get_random_string


class Services:

    @staticmethod
    @transaction.atomic
    def CreateIdentity(key, is_virtual=False, user=None):
        identity = Identity(key=key.lower(), user=user, is_virtual=is_virtual)
        identity.save()
        identity.refresh_from_db()
        return identity

    @staticmethod
    @transaction.atomic
    def SetEmailInvalid(identity):
        identity.email_is_valid = False
        identity.save()
        return identity

    @staticmethod
    @transaction.atomic
    def AssociateIdentity(identity, user):
        identity.user = user
        identity.save()
        return identity

    @staticmethod
    @transaction.atomic
    def ChangeKey(identity, new_key, is_virtual=False):
        identity.key = new_key.lower()
        identity.is_virtual = is_virtual
        identity.save()
        return identity

    @staticmethod
    def GenerateUniqueKey():
        key = get_random_string(length=5).lower()
        if Identity.objects.filter(key=key).count() > 0:
            return Services.GenerateUniqueKey()
        return key
