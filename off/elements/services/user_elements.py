from off.infrastructure import services as infra
from off.elements.models import UserElement
from django.db import transaction


class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self._user_element = self.get_user_element()

    @transaction.atomic
    def get_user_element(self):
        if not self._user_element:
            self._user_element = UserElement.objects.get_or_create(user=self.user)[0]
        return self._user_element
