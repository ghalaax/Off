from off.infrastructure import services as infra
from off.elements.models import UserElement
from django.db import transaction


class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self._user_element = self.get_user_element()

    def get_user_element(self):
        if not self._user_element:
            try:
                self._user_element = UserElement.objects.get(user=self.user)
            except UserElement.DoesNotExist:
                self._user_element = self.__create_user_element__()
        return self._user_element

    @transaction.atomic
    def __create_user_element__(self):
        return UserElement.objects.create(user=self.user)
