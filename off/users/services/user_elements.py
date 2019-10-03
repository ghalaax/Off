from off.infrastructure import services as infra
from off.elements.models import UserElement
from off.elements.services import shapes, elements
from off.elements.constants import BuiltinSemantics
from off.users.constants import Shapes
from django.db import transaction


class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self._user_element = self.get_user_element()
        self.shapes_services = shapes.Services.fromContext(context)
        self.element_services = elements.Services.fromContext(context)

    @transaction.atomic
    def get_user_element(self):
        """
        Gets or creates the current user UserElement
        """
        if not self._user_element:
            (self._user_element, created) = UserElement.objects.get_or_create(
                user=self.user)
            if created:
                self.__link_user_element_to_user_shape__(self._user_element)
        return self._user_element

    @transaction.atomic
    def __link_user_element_to_user_shape__(self, user_element):
        shape = self.shapes_services.create_shape(Shapes.user.value, str(Shapes.user))
        source = self.element_services.get_source_element()
        return self.element_services.link_to_element(source, shape, user_element)

    def set_element_creator(self, element):
        """
        Adds the ```creates``` builtin to the link between the user and the element
        """
        creates_builtin = self.element_services.get_builtin(BuiltinSemantics.creates)
        return self.element_services.link_to_element(self.get_user_element(),
                                                     creates_builtin, element)
